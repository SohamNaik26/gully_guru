import os
import csv
import json
import httpx
import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from sqlmodel import Session, select

from src.models.cricsheet import (
    CricsheetPlayer, CricsheetMatch, CricsheetInnings, CricsheetPlayerPerformance
)
from src.db.models import (
    Player, Match, MatchPerformance, PlayerStats
)
from src.db.session import get_session, get_async_session


class CricsheetClient:
    """Client for interacting with Cricsheet data."""
    
    BASE_URL = "https://cricsheet.org/downloads"
    REGISTRY_URL = "https://cricsheet.org/registry"
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the Cricsheet client.
        
        Args:
            cache_dir: Directory to cache downloaded files (default: ~/.cricsheet)
        """
        self.cache_dir = cache_dir or os.path.expanduser("~/.cricsheet")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def _download_file(self, url: str, output_path: Path) -> bool:
        """
        Download a file from a URL.
        
        Args:
            url: URL to download from
            output_path: Path to save the file
            
        Returns:
            True if download was successful, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                # Create parent directories if they don't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write content to file
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                return True
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return False
    
    async def download_ipl_data(self, year: int) -> Path:
        """
        Download IPL data for a specific year.
        
        Args:
            year: IPL season year
            
        Returns:
            Path to the downloaded file
        """
        url = f"{self.BASE_URL}/ipl/json/ipl_{year}.zip"
        output_path = Path(self.cache_dir) / f"ipl_{year}.zip"
        
        if not output_path.exists():
            success = await self._download_file(url, output_path)
            if not success:
                raise ValueError(f"Failed to download IPL {year} data")
        
        return output_path
    
    async def download_player_registry(self) -> Path:
        """
        Download the player registry.
        
        Returns:
            Path to the downloaded file
        """
        url = f"{self.REGISTRY_URL}/people.csv"
        output_path = Path(self.cache_dir) / "people.csv"
        
        if not output_path.exists() or (datetime.now() - datetime.fromtimestamp(output_path.stat().st_mtime)).days > 7:
            success = await self._download_file(url, output_path)
            if not success:
                raise ValueError("Failed to download player registry")
        
        return output_path
    
    async def download_match_registry(self) -> Path:
        """
        Download the match registry.
        
        Returns:
            Path to the downloaded file
        """
        url = f"{self.REGISTRY_URL}/matches.csv"
        output_path = Path(self.cache_dir) / "matches.csv"
        
        if not output_path.exists() or (datetime.now() - datetime.fromtimestamp(output_path.stat().st_mtime)).days > 7:
            success = await self._download_file(url, output_path)
            if not success:
                raise ValueError("Failed to download match registry")
        
        return output_path
    
    async def load_player_data(self) -> List[CricsheetPlayer]:
        """
        Load player data from the registry.
        
        Returns:
            List of CricsheetPlayer objects
        """
        player_registry_path = await self.download_player_registry()
        
        try:
            # Read CSV using pandas
            df = pd.read_csv(player_registry_path)
            
            # Process the data
            players = []
            for _, row in df.iterrows():
                # Convert row to dictionary and handle missing values
                player_data = row.to_dict()
                
                # Process teams (might be a comma-separated string)
                if "teams" in player_data and isinstance(player_data["teams"], str):
                    player_data["teams"] = [team.strip() for team in player_data["teams"].split(",")]
                else:
                    player_data["teams"] = []
                
                # Convert DOB to datetime if present
                if "dob" in player_data and pd.notna(player_data["dob"]):
                    try:
                        player_data["dob"] = datetime.strptime(player_data["dob"], "%Y-%m-%d")
                    except:
                        player_data["dob"] = None
                
                # Create CricsheetPlayer object
                try:
                    player = CricsheetPlayer(**player_data)
                    players.append(player)
                except Exception as e:
                    print(f"Error processing player {player_data.get('name', 'unknown')}: {str(e)}")
            
            return players
        
        except Exception as e:
            raise ValueError(f"Error loading player data: {str(e)}")
    
    async def load_match_data(self, competition: str = "ipl") -> List[CricsheetMatch]:
        """
        Load match data from the registry.
        
        Args:
            competition: Competition to filter by (default: ipl)
            
        Returns:
            List of CricsheetMatch objects
        """
        match_registry_path = await self.download_match_registry()
        
        try:
            # Read CSV using pandas
            df = pd.read_csv(match_registry_path)
            
            # Filter by competition if specified
            if competition:
                df = df[df["competition"].str.lower() == competition.lower()]
            
            # Process the data
            matches = []
            for _, row in df.iterrows():
                # Convert row to dictionary and handle missing values
                match_data = row.to_dict()
                
                # Convert date to datetime
                if "date" in match_data and pd.notna(match_data["date"]):
                    try:
                        match_data["date"] = datetime.strptime(match_data["date"], "%Y-%m-%d")
                    except:
                        match_data["date"] = None
                
                # Create CricsheetMatch object
                try:
                    match = CricsheetMatch(**match_data)
                    matches.append(match)
                except Exception as e:
                    print(f"Error processing match {match_data.get('key', 'unknown')}: {str(e)}")
            
            return matches
        
        except Exception as e:
            raise ValueError(f"Error loading match data: {str(e)}")


async def import_cricsheet_players(session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Import players from Cricsheet to the database.
    
    Args:
        session: Database session (optional)
        
    Returns:
        Dictionary with import results
    """
    close_session = False
    if session is None:
        session = next(get_session())
        close_session = True
    
    try:
        # Initialize client and load player data
        client = CricsheetClient()
        cricsheet_players = await client.load_player_data()
        
        # Filter for IPL players only
        ipl_players = [p for p in cricsheet_players if "IPL" in p.teams or any(t in p.teams for t in ["RCB", "MI", "CSK", "KKR", "DC", "PBKS", "RR", "SRH", "GT", "LSG"])]
        
        # Check for existing players to avoid duplicates
        existing_keys = session.exec(
            select(Player.cricsheet_key).where(Player.cricsheet_key.isnot(None))
        ).all()
        existing_keys_set = set(existing_keys)
        
        # Convert to database models
        new_players = []
        updated_players = []
        
        for cp in ipl_players:
            if cp.key in existing_keys_set:
                # Update existing player
                db_player = session.exec(
                    select(Player).where(Player.cricsheet_key == cp.key)
                ).one()
                
                # Update fields
                db_player.name = cp.name
                db_player.known_as = cp.known_as
                db_player.dob = cp.dob
                db_player.batting_style = cp.batting_style
                db_player.bowling_style = cp.bowling_style
                
                updated_players.append(db_player)
            else:
                # Create new player
                player_data = cp.to_db_model()
                db_player = Player(**player_data)
                new_players.append(db_player)
        
        # Bulk insert new players
        if new_players:
            session.add_all(new_players)
        
        # Commit changes
        session.commit()
        
        # Return results
        return {
            "success": True,
            "new_players_count": len(new_players),
            "updated_players_count": len(updated_players),
            "total_players_processed": len(ipl_players)
        }
    
    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        if close_session:
            session.close()


async def import_cricsheet_matches(session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Import matches from Cricsheet to the database.
    
    Args:
        session: Database session (optional)
        
    Returns:
        Dictionary with import results
    """
    close_session = False
    if session is None:
        session = next(get_session())
        close_session = True
    
    try:
        # Initialize client and load match data
        client = CricsheetClient()
        cricsheet_matches = await client.load_match_data(competition="ipl")
        
        # Check for existing matches to avoid duplicates
        existing_keys = session.exec(
            select(Match.cricsheet_key).where(Match.cricsheet_key.isnot(None))
        ).all()
        existing_keys_set = set(existing_keys)
        
        # Convert to database models
        new_matches = []
        updated_matches = []
        
        for cm in cricsheet_matches:
            if cm.key in existing_keys_set:
                # Update existing match
                db_match = session.exec(
                    select(Match).where(Match.cricsheet_key == cm.key)
                ).one()
                
                # Update fields
                db_match.date = cm.date
                db_match.venue = cm.venue
                db_match.city = cm.city
                db_match.team1 = cm.team1
                db_match.team2 = cm.team2
                db_match.toss_winner = cm.toss_winner
                db_match.toss_decision = cm.toss_decision
                db_match.winner = cm.winner
                db_match.result = cm.result
                db_match.result_margin = cm.result_margin
                
                updated_matches.append(db_match)
            else:
                # Create new match
                match_data = cm.to_db_model()
                db_match = Match(**match_data)
                new_matches.append(db_match)
        
        # Bulk insert new matches
        if new_matches:
            session.add_all(new_matches)
        
        # Commit changes
        session.commit()
        
        # Return results
        return {
            "success": True,
            "new_matches_count": len(new_matches),
            "updated_matches_count": len(updated_matches),
            "total_matches_processed": len(cricsheet_matches)
        }
    
    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        if close_session:
            session.close()


async def process_match_performances(match_key: str, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Process player performances for a specific match.
    
    Args:
        match_key: Cricsheet match key
        session: Database session (optional)
        
    Returns:
        Dictionary with processing results
    """
    # Implementation would parse the JSON match file and extract player performances
    # This is a complex task that would require parsing the ball-by-ball data
    # For brevity, we're providing a skeleton implementation
    
    # The full implementation would:
    # 1. Download and parse the JSON match file
    # 2. Extract batting and bowling performances
    # 3. Calculate fantasy points based on performance
    # 4. Update player stats and match performances in the database
    
    pass


async def update_player_stats_from_performances(player_id: int, session: Optional[Session] = None) -> Dict[str, Any]:
    """
    Update a player's cumulative stats based on their match performances.
    
    Args:
        player_id: Player ID
        session: Database session (optional)
        
    Returns:
        Dictionary with update results
    """
    close_session = False
    if session is None:
        session = next(get_session())
        close_session = True
    
    try:
        # Get all performances for the player
        performances = session.exec(
            select(MatchPerformance).where(MatchPerformance.player_id == player_id)
        ).all()
        
        if not performances:
            return {
                "success": True,
                "message": f"No performances found for player {player_id}"
            }
        
        # Calculate cumulative stats
        total_runs = sum(p.runs_scored for p in performances)
        total_wickets = sum(p.wickets for p in performances)
        highest_score = max((p.runs_scored for p in performances), default=0)
        
        # Find best bowling performance
        best_bowling_wickets = 0
        best_bowling_runs = float('inf')
        
        for p in performances:
            if p.wickets > best_bowling_wickets or (p.wickets == best_bowling_wickets and p.runs_conceded < best_bowling_runs):
                best_bowling_wickets = p.wickets
                best_bowling_runs = p.runs_conceded
        
        best_bowling = f"{best_bowling_wickets}/{best_bowling_runs}" if best_bowling_wickets > 0 else "0/0"
        
        # Get or create player stats
        player_stats = session.exec(
            select(PlayerStats).where(PlayerStats.player_id == player_id)
        ).first()
        
        if player_stats:
            # Update existing stats
            player_stats.matches_played = len(performances)
            player_stats.runs = total_runs
            player_stats.wickets = total_wickets
            player_stats.highest_score = highest_score
            player_stats.best_bowling = best_bowling
            # Fantasy points calculation would go here
        else:
            # Create new stats
            player_stats = PlayerStats(
                player_id=player_id,
                matches_played=len(performances),
                runs=total_runs,
                wickets=total_wickets,
                highest_score=highest_score,
                best_bowling=best_bowling
                # Fantasy points calculation would go here
            )
            session.add(player_stats)
        
        # Commit changes
        session.commit()
        
        return {
            "success": True,
            "player_id": player_id,
            "matches_played": len(performances),
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "highest_score": highest_score,
            "best_bowling": best_bowling
        }
    
    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        if close_session:
            session.close()


async def main():
    """Main function to run the Cricsheet integration."""
    # Import players
    player_result = await import_cricsheet_players()
    print(f"Player import result: {player_result}")
    
    # Import matches
    match_result = await import_cricsheet_matches()
    print(f"Match import result: {match_result}")
    
    # Process match performances and update player stats
    # This would be implemented in a production system
    
    print("Cricsheet integration completed")


if __name__ == "__main__":
    asyncio.run(main()) 