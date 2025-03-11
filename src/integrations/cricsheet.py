import os
import httpx
import asyncio
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging
import traceback

from sqlmodel import Session, select

from src.db.models.cricsheet import CricsheetPlayer, CricsheetMatch
from src.db.models import Player, Match, MatchPerformance
from src.db.session import get_session, engine
from src.db.integration_helper import (
    push_integration_data,
    process_integration_data,
    retry_operation,
)
from src.utils.logger import get_logger

logger = logging.getLogger(__name__)


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

        if (
            not output_path.exists()
            or (
                datetime.now() - datetime.fromtimestamp(output_path.stat().st_mtime)
            ).days
            > 7
        ):
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

        if (
            not output_path.exists()
            or (
                datetime.now() - datetime.fromtimestamp(output_path.stat().st_mtime)
            ).days
            > 7
        ):
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
                    player_data["teams"] = [
                        team.strip() for team in player_data["teams"].split(",")
                    ]
                else:
                    player_data["teams"] = []

                # Convert DOB to datetime if present
                if "dob" in player_data and pd.notna(player_data["dob"]):
                    try:
                        player_data["dob"] = datetime.strptime(
                            player_data["dob"], "%Y-%m-%d"
                        )
                    except:
                        player_data["dob"] = None

                # Create CricsheetPlayer object
                try:
                    player = CricsheetPlayer(**player_data)
                    players.append(player)
                except Exception as e:
                    print(
                        f"Error processing player {player_data.get('name', 'unknown')}: {str(e)}"
                    )

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
                        match_data["date"] = datetime.strptime(
                            match_data["date"], "%Y-%m-%d"
                        )
                    except:
                        match_data["date"] = None

                # Create CricsheetMatch object
                try:
                    match = CricsheetMatch(**match_data)
                    matches.append(match)
                except Exception as e:
                    print(
                        f"Error processing match {match_data.get('key', 'unknown')}: {str(e)}"
                    )

            return matches

        except Exception as e:
            raise ValueError(f"Error loading match data: {str(e)}")


async def import_cricsheet_players_data():
    """
    Import player data from Cricsheet to PostgreSQL database.

    Returns:
        bool: True if import was successful, False otherwise
    """
    try:
        # This is a placeholder - replace with actual Cricsheet API call
        logger.info("Fetching data from Cricsheet...")

        # Example of fetching data from an API
        response = await retry_operation(
            lambda: requests.get("https://cricsheet.org/api/players.json")
        )

        if response.status_code != 200:
            logger.error(f"Failed to fetch data: {response.status_code}")
            return False

        players_data = response.json()

        # Process data and create records
        import_records = []
        for player_id, player_info in players_data.items():
            import_records.append(
                {
                    "external_id": player_id,
                    "name": player_info.get("name", "Unknown"),
                    "team": player_info.get("team", "Unknown"),
                    "import_date": datetime.now(timezone.utc),
                    "processed": False,
                }
            )

        # Push data to integration table
        success = await push_integration_data(
            CricsheetPlayer, import_records, strategy="replace"
        )

        if success:
            # Process the imports
            await process_cricsheet_imports()
            return True
        else:
            return False

    except Exception as e:
        logger.error(f"Error importing Cricsheet data: {str(e)}")
        logger.error(f"Detailed error:\n{traceback.format_exc()}")
        return False


async def cricsheet_to_player_processor(cricsheet_record, session):
    """Process a CricsheetPlayer record into a Player record."""
    try:
        # Skip records with missing essential data
        if not cricsheet_record.name or cricsheet_record.name == "Unknown":
            logger.warning(f"Skipping record {cricsheet_record.id} with missing name")
            cricsheet_record.processed = True
            cricsheet_record.status = "skipped"
            session.add(cricsheet_record)
            return None

        # Check if player already exists by external ID
        player_result = await session.execute(
            select(Player)
            .join(CricsheetPlayer)
            .where(CricsheetPlayer.external_id == cricsheet_record.external_id)
        )
        player = player_result.scalar_one_or_none()

        # If not found by external ID, try by name
        if not player:
            player_result = await session.execute(
                select(Player).where(Player.name == cricsheet_record.name)
            )
            player = player_result.scalar_one_or_none()

        if player:
            # Update existing player
            player.updated_at = datetime.now(timezone.utc)
            session.add(player)

            # Link import to player
            cricsheet_record.player_id = player.id
            cricsheet_record.processed = True
            cricsheet_record.status = "updated"
            session.add(cricsheet_record)

            return player
        else:
            # Create new player
            player = Player(
                name=cricsheet_record.name,
                team=cricsheet_record.team,
                player_type="Unknown",  # Cricsheet might not provide this
                season=2025,  # Default to current season
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(player)
            await session.flush()  # Get the ID

            # Link import to player
            cricsheet_record.player_id = player.id
            cricsheet_record.processed = True
            cricsheet_record.status = "created"
            session.add(cricsheet_record)

            return player

    except Exception as e:
        logger.error(
            f"Error processing Cricsheet record {cricsheet_record.id}: {str(e)}"
        )
        cricsheet_record.status = "failed"
        session.add(cricsheet_record)
        raise


async def process_cricsheet_imports():
    """Process imported Cricsheet data into Player records."""
    stats = await process_integration_data(
        CricsheetPlayer,
        Player,
        cricsheet_to_player_processor,
        condition=CricsheetPlayer.processed == False,
    )

    logger.info(
        f"Processed Cricsheet player imports: "
        f"{stats['created']} created, {stats['updated']} updated, "
        f"{stats['skipped']} skipped, {stats['failed']} failed"
    )

    return stats


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
            "total_matches_processed": len(cricsheet_matches),
        }

    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}

    finally:
        if close_session:
            session.close()


async def process_match_performances(
    match_key: str, session: Optional[Session] = None
) -> Dict[str, Any]:
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


async def update_player_stats_from_performances(
    player_id: int, session: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Update player statistics based on match performances.

    This function calculates aggregate statistics for a player based on their
    match performances and updates the database.

    Args:
        player_id: The ID of the player to update stats for
        session: Optional database session

    Returns:
        Dict with status information
    """
    logger = get_logger()
    close_session = False

    if not session:
        session = Session(engine)
        close_session = True

    try:
        # Get player
        player = session.get(Player, player_id)
        if not player:
            return {
                "status": "error",
                "message": f"Player with ID {player_id} not found",
            }

        # Get all performances for this player
        performances = session.exec(
            select(MatchPerformance).where(MatchPerformance.player_id == player_id)
        ).all()

        if not performances:
            logger.info(f"No performances found for player {player_id}")
            return {"status": "success", "message": "No performances to process"}

        # Calculate stats
        total_runs = sum(
            p.runs_scored for p in performances if p.runs_scored is not None
        )
        total_wickets = sum(
            p.wickets_taken for p in performances if p.wickets_taken is not None
        )

        # Calculate highest score
        highest_score = max(
            (p.runs_scored for p in performances if p.runs_scored is not None),
            default=0,
        )

        # Calculate best bowling
        best_bowling_performances = [
            (p.wickets_taken, p.runs_conceded)
            for p in performances
            if p.wickets_taken is not None
            and p.wickets_taken > 0
            and p.runs_conceded is not None
        ]

        best_bowling = (
            f"{max(best_bowling_performances, key=lambda x: (x[0], -x[1]))[0]}/"
            f"{max(best_bowling_performances, key=lambda x: (x[0], -x[1]))[1]}"
            if best_bowling_performances
            else "0/0"
        )

        # Instead of updating PlayerStats, we just log the calculated stats
        logger.info(f"Player {player.name} (ID: {player_id}) stats calculated:")
        logger.info(f"Matches played: {len(performances)}")
        logger.info(f"Total runs: {total_runs}")
        logger.info(f"Total wickets: {total_wickets}")
        logger.info(f"Highest score: {highest_score}")
        logger.info(f"Best bowling: {best_bowling}")

        return {
            "status": "success",
            "player_id": player_id,
            "player_name": player.name,
            "matches_played": len(performances),
            "runs": total_runs,
            "wickets": total_wickets,
            "highest_score": highest_score,
            "best_bowling": best_bowling,
        }

    except Exception as e:
        logger.error(f"Error updating player stats: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        if close_session:
            session.close()


async def main():
    """Main function to run the Cricsheet integration."""
    # Import players
    player_result = await import_cricsheet_players_data()
    print(f"Player import result: {player_result}")

    # Import matches
    match_result = await import_cricsheet_matches()
    print(f"Match import result: {match_result}")

    # Process match performances and update player stats
    # This would be implemented in a production system

    print("Cricsheet integration completed")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the import
    asyncio.run(main())
