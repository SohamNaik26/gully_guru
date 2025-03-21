# IPL fixtures integration for https://fixturedownload.com/feed/json/ipl-2025

import httpx
import asyncio
import logging
import traceback
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from sqlmodel import select
from sqlalchemy import func, and_
from contextlib import asynccontextmanager
import pandas as pd
import sqlalchemy

from src.db.models.ipl_fixures import IPLMatch, MatchInput, TeamEnum, IPLRound
from src.db.session import get_session

logger = logging.getLogger(__name__)


# Helper context manager to get a session
@asynccontextmanager
async def get_db_session():
    """Context manager to get a database session"""
    session_gen = get_session()
    try:
        session = await anext(session_gen)
        try:
            yield session
        finally:
            await session.close()
    finally:
        try:
            await session_gen.aclose()
        except Exception:
            pass


async def fetch_fixtures(season: str = "2025") -> Optional[List[Dict]]:
    """Fetch IPL fixtures data from fixturedownload.com"""
    url = f"https://fixturedownload.com/feed/json/ipl-{season}"

    try:
        logger.info(f"Fetching fixtures from {url}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            fixtures = response.json()
            logger.info(f"Fetched {len(fixtures)} fixtures for IPL {season}")
            return fixtures
    except Exception as e:
        logger.error(f"Failed to fetch fixtures: {e}")
        logger.error(traceback.format_exc())
        return None


def transform_fixtures(fixtures: List[Dict], season: str = "2025") -> List[Dict]:
    """Transform API fixtures data to database model format"""
    season_int = int(season)
    matches = []
    now = datetime.now(timezone.utc)  # Keep timezone info to match TimeStampedModel

    for fixture in fixtures:
        try:
            # Parse with Pydantic model for validation
            match_input = MatchInput(**fixture)

            # Keep datetimes timezone-aware to match TimeStampedModel
            date_utc = match_input.DateUtc
            if date_utc.tzinfo is None:
                date_utc = date_utc.replace(tzinfo=timezone.utc)

            # Calculate IST by adding the offset to UTC time
            ist_offset = timedelta(hours=5, minutes=30)
            date_ist = date_utc.astimezone(timezone.utc) + ist_offset

            # Get team codes
            home_team_code = TeamEnum.get_short_code(match_input.HomeTeam)
            away_team_code = TeamEnum.get_short_code(match_input.AwayTeam)

            matches.append(
                {
                    "match_number": match_input.MatchNumber,
                    "round_number": match_input.RoundNumber,
                    "date_utc": date_utc,
                    "date_ist": date_ist,
                    "location": match_input.Location,
                    "home_team": match_input.HomeTeam,
                    "away_team": match_input.AwayTeam,
                    "home_team_code": home_team_code,
                    "away_team_code": away_team_code,
                    "group": match_input.Group,
                    "home_team_score": match_input.HomeTeamScore,
                    "away_team_score": match_input.AwayTeamScore,
                    "season": season_int,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        except Exception as e:
            logger.error(f"Error processing fixture: {e}")

    return matches


async def store_fixtures(records: List[Dict]) -> bool:
    """Store IPL fixtures in the database with upsert logic"""
    if not records:
        logger.warning("No fixtures to store")
        return True

    try:
        async with get_db_session() as session:
            for record in records:
                # Check if fixture exists
                query = select(IPLMatch).where(
                    (IPLMatch.match_number == record["match_number"])
                    & (IPLMatch.season == record["season"])
                )
                result = await session.execute(query)
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing record
                    for key, value in record.items():
                        if key not in ["id", "created_at"]:
                            setattr(existing, key, value)
                else:
                    # Create new record
                    session.add(IPLMatch(**record))

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        logger.error(traceback.format_exc())
        return False


async def import_fixtures(season: str = "2025") -> bool:
    """Import IPL fixtures data for a specific season"""
    try:
        # Extract: Fetch data from API
        fixtures = await fetch_fixtures(season)
        if not fixtures:
            return False

        # Transform: Convert to database model format
        transformed_fixtures = transform_fixtures(fixtures, season)
        if not transformed_fixtures:
            logger.error("No valid fixtures found to import")
            return False

        # Load: Store in database
        success = await store_fixtures(transformed_fixtures)
        if success:
            logger.info(
                f"Successfully imported {len(transformed_fixtures)} fixtures for IPL {season}"
            )

        return success
    except Exception as e:
        logger.error(f"Error importing fixtures: {e}")
        logger.error(traceback.format_exc())
        return False


async def filter_by_team(
    season: str = "2025", team: Optional[str] = None
) -> List[Dict]:
    """Filter fixtures by team name or code"""
    async with get_db_session() as session:
        query = select(IPLMatch).where(IPLMatch.season == int(season))

        if team:
            # Check if input is a team code
            if team.upper() in TeamEnum.__members__:
                team_code = team.upper()
                query = query.where(
                    (IPLMatch.home_team_code == team_code)
                    | (IPLMatch.away_team_code == team_code)
                )
            else:
                # Assume it's a team name or partial name
                team_lower = f"%{team.lower()}%"
                query = query.where(
                    func.lower(IPLMatch.home_team).like(team_lower)
                    | func.lower(IPLMatch.away_team).like(team_lower)
                )

        result = await session.execute(query)
        fixtures = result.scalars().all()

        # Return in API format
        return [
            {
                "MatchNumber": f.match_number,
                "RoundNumber": f.round_number,
                "DateUtc": f.date_utc.isoformat(),
                "Location": f.location,
                "HomeTeam": f.home_team,
                "AwayTeam": f.away_team,
                "Group": f.group,
                "HomeTeamScore": f.home_team_score,
                "AwayTeamScore": f.away_team_score,
            }
            for f in fixtures
        ]


async def create_balanced_rounds(
    season: str = "2025", off_by_match: int = 1, spacing: int = 7
) -> bool:
    """
    Generate balanced rounds for IPL fixtures and store them in the database.

    Uses a statistical approach to find optimal round boundaries where all teams
    have played a similar number of matches.

    Args:
        season: The IPL season to create rounds for
        off_by_match: Tolerance for match count differences
        spacing: Ideal spacing between round boundaries

    Returns:
        bool: Success status
    """
    logger.info(f"Generating balanced rounds for IPL {season}")

    try:
        # 1. Get match data with team play counts from DB
        team_match_counts = await get_team_match_counts_by_match_number(season)

        if team_match_counts.empty:
            logger.error("No match data available to generate rounds")
            return False

        # 2. Find optimal round boundaries
        round_boundaries = await calculate_optimal_round_boundaries(
            team_match_counts, off_by_match=off_by_match, spacing=spacing
        )
        if round_boundaries.empty:
            logger.error("Failed to calculate optimal round boundaries")
            return False

        # 3. Create round summary data
        rounds_summary = await create_rounds_summary(
            team_match_counts, round_boundaries
        )
        if rounds_summary.empty:
            logger.error("Failed to create rounds summary")
            return False

        # 4. Fetch actual match timestamps
        rounds_with_dates = await add_match_timestamps_to_rounds(rounds_summary, season)
        if rounds_with_dates.empty:
            logger.error("Failed to add timestamps to rounds")
            return False

        # 5. Store in database
        success = await store_balanced_rounds(rounds_with_dates, season)
        if success:
            # 6. Update matches with their game round info
            await update_matches_with_game_rounds(season)
            logger.info(
                f"Successfully created {len(rounds_with_dates)} balanced rounds for IPL {season}"
            )

        return success

    except Exception as e:
        logger.error(f"Error creating balanced rounds: {e}")
        logger.error(traceback.format_exc())
        return False


async def get_team_match_counts_by_match_number(season: str) -> pd.DataFrame:
    """
    Get data about how many matches each team has played by each match number.

    Returns:
        pd.DataFrame: DataFrame with columns ['team', 'match_number', 'cumulative_matches_played']
    """
    logger.info(f"Fetching team match counts for season {season}")

    try:
        # We need to construct a dataframe showing cumulative match counts for each team
        # up to each match number
        async with get_db_session() as session:
            # First get all matches for the season ordered by match number with number <= 70
            query = (
                select(IPLMatch)
                .where(IPLMatch.season == int(season))
                .where(IPLMatch.match_number <= 70)
                .order_by(IPLMatch.match_number)
            )

            result = await session.execute(query)
            matches = result.scalars().all()

            if not matches:
                return pd.DataFrame()

            # Create dataframe structure
            data = []

            # Get all unique match numbers
            match_numbers = sorted(list(set(m.match_number for m in matches)))

            # Get all team codes
            team_codes = list(TeamEnum.__members__.keys())

            # Initialize match counts
            team_match_counts = {team: 0 for team in team_codes}

            # Process each match
            for match_num in match_numbers:
                # Find all matches up to this match number
                matches_up_to = [m for m in matches if m.match_number <= match_num]

                # Reset counts for this iteration
                for team in team_codes:
                    team_match_counts[team] = 0

                # Count home and away matches for each team
                for match in matches_up_to:
                    if match.home_team_code in team_match_counts:
                        team_match_counts[match.home_team_code] += 1
                    if match.away_team_code in team_match_counts:
                        team_match_counts[match.away_team_code] += 1

                # Add counts to data
                for team, count in team_match_counts.items():
                    data.append(
                        {
                            "team": team,
                            "match_number": match_num,
                            "cumulative_matches_played": count,
                        }
                    )

            return pd.DataFrame(data)

    except Exception as e:
        logger.error(f"Error getting team match counts: {e}")
        logger.error(traceback.format_exc())
        return pd.DataFrame()


async def calculate_optimal_round_boundaries(
    df: pd.DataFrame, off_by_match: int = 1, spacing: int = 7
) -> pd.DataFrame:
    """
    Calculate optimal match numbers to use as round boundaries.

    Args:
        df: DataFrame with team match counts
        off_by_match: Tolerance for match count differences
        spacing: Ideal spacing between round boundaries

    Returns:
        pd.DataFrame: Selected round boundary match numbers with statistics
    """
    logger.info("Calculating optimal round boundaries")

    if df.empty:
        return pd.DataFrame()

    # Convert data types
    df["cumulative_matches_played"] = pd.to_numeric(df["cumulative_matches_played"])

    # Group by match_number and calculate statistics
    match_stats = df.groupby("match_number").agg(
        {"cumulative_matches_played": ["min", "max", "mean", "std"]}
    )

    # Flatten columns
    match_stats.columns = ["min_matches", "max_matches", "avg_matches", "std_matches"]

    # Calculate balance metrics
    match_stats["range"] = match_stats["max_matches"] - match_stats["min_matches"]
    match_stats["within_tolerance"] = match_stats["range"] <= off_by_match
    match_stats["cv"] = match_stats["std_matches"] / match_stats["avg_matches"].replace(
        0, 1e-10
    )
    match_stats["balance_score"] = (0.7 * match_stats["range"]) + (
        0.3 * match_stats["cv"]
    )
    match_stats.loc[match_stats["within_tolerance"], "balance_score"] *= 0.5

    # Reset index
    match_stats = match_stats.reset_index()

    # Select well-distributed match numbers
    selected_matches = []
    candidates = match_stats[match_stats["within_tolerance"]].copy()

    if len(candidates) < 5:
        candidates = match_stats.copy()

    candidates = candidates.sort_values("balance_score")

    # First match
    early_matches = candidates[candidates["match_number"] <= 15]
    if not early_matches.empty:
        selected_matches.append(early_matches.iloc[0]["match_number"])
    else:
        selected_matches.append(candidates.iloc[0]["match_number"])

    # Remaining matches with good spacing
    max_match = match_stats["match_number"].max()
    while True:
        last = selected_matches[-1]

        # Calculate remaining matches to the end
        remaining_matches = max_match - last

        # Dynamically adjust spacing based on remaining matches
        if remaining_matches < spacing * 2:
            # When we're getting close to the end, use a smaller spacing
            # But never go below 3 matches to maintain meaningful rounds
            current_spacing = max(3, remaining_matches // 2)
        else:
            # Otherwise use normal spacing
            current_spacing = spacing

        # Calculate range with dynamic spacing
        next_range = (last + current_spacing - 2, last + current_spacing + 2)

        # Find candidates in the adjusted range
        in_range = candidates[
            (candidates["match_number"] > next_range[0])
            & (candidates["match_number"] <= next_range[1])
        ]

        if not in_range.empty:
            selected_matches.append(in_range.iloc[0]["match_number"])
        else:
            # Try with a wider range, proportional to the current spacing
            wider_range = (last + current_spacing - 4, last + current_spacing + 4)
            wider_in_range = candidates[
                (candidates["match_number"] > wider_range[0])
                & (candidates["match_number"] <= wider_range[1])
            ]

            if not wider_in_range.empty:
                selected_matches.append(wider_in_range.iloc[0]["match_number"])
            else:
                # Special handling for approaching the end
                if remaining_matches > 3:
                    # Take any good candidate after the current position
                    next_matches = candidates[candidates["match_number"] > last + 3]
                    if not next_matches.empty:
                        selected_matches.append(next_matches.iloc[0]["match_number"])
                    else:
                        # No good candidates - we might need to relax balance criteria
                        remaining_candidates = match_stats[
                            (match_stats["match_number"] > last + 3)
                            & (match_stats["match_number"] <= max_match)
                        ].reset_index()

                        if not remaining_candidates.empty:
                            # Take the best candidate from what's left, even if not perfect
                            best_remaining = remaining_candidates.sort_values(
                                "balance_score"
                            ).iloc[0]
                            selected_matches.append(best_remaining["match_number"])
                        else:
                            break
                else:
                    # We're very close to the end - add the last match if not already included
                    if max_match not in selected_matches:
                        selected_matches.append(max_match)
                    break

        # Modified stopping condition - only stop when we've reached the end
        if selected_matches[-1] >= max_match:
            break

        # Keep the maximum rounds limit as a safety valve
        if len(selected_matches) >= 10:
            # But always ensure the last match is included
            if max_match not in selected_matches:
                selected_matches.append(max_match)
            break

    # Return selected match data
    return match_stats[match_stats["match_number"].isin(selected_matches)].sort_values(
        "match_number"
    )


async def create_rounds_summary(
    df: pd.DataFrame, round_boundaries: pd.DataFrame
) -> pd.DataFrame:
    """
    Create a summary table of rounds with team-specific metrics based on selected boundaries.

    Args:
        df: DataFrame with team match counts
        round_boundaries: DataFrame with selected round boundary match numbers

    Returns:
        pd.DataFrame: Summary of rounds with metrics
    """
    logger.info("Creating rounds summary")

    if df.empty or round_boundaries.empty:
        return pd.DataFrame()

    # Get list of match numbers
    selected_matches = round_boundaries["match_number"].tolist()

    # Prepare rounds data
    selected_matches_with_zero = [0] + selected_matches
    rounds_data = []
    teams = sorted(df["team"].unique())

    for i in range(1, len(selected_matches_with_zero)):
        boundary_start = selected_matches_with_zero[i - 1]
        boundary_end = selected_matches_with_zero[i]

        # Initialize round data with inclusive first and last match numbers
        round_data = {
            "round_number": i,
            "first_match": boundary_start + 1,  # First match in round (inclusive)
            "last_match": boundary_end,  # Last match in round (inclusive)
            "matches_in_round": boundary_end - boundary_start,
        }

        # Initialize team_matches dictionary
        team_matches_dict = {}
        all_team_matches = []

        for team in teams:
            team_df = df[df["team"] == team]

            # Get start and end counts
            start_count = 0
            if boundary_start > 0:
                start_rows = team_df[team_df["match_number"] == boundary_start]
                if not start_rows.empty:
                    start_count = start_rows["cumulative_matches_played"].values[0]

            end_rows = team_df[team_df["match_number"] == boundary_end]
            end_count = 0
            if not end_rows.empty:
                end_count = end_rows["cumulative_matches_played"].values[0]

            # Calculate matches in this round for this team and convert to integer
            matches_in_round = int(end_count - start_count)
            team_matches_dict[team] = matches_in_round
            all_team_matches.append(matches_in_round)

        # Add the team_matches dictionary to round data
        round_data["team_matches"] = team_matches_dict

        # Add overall round statistics (converted to integers)
        if all_team_matches:
            round_data["min_team_matches"] = int(min(all_team_matches))
            round_data["max_team_matches"] = int(max(all_team_matches))
            round_data["is_balanced"] = (
                round_data["min_team_matches"] == round_data["max_team_matches"]
            )

        rounds_data.append(round_data)

    return pd.DataFrame(rounds_data)


async def add_match_timestamps_to_rounds(
    rounds_df: pd.DataFrame, season: str
) -> pd.DataFrame:
    """
    Add actual match timestamps to round boundaries by looking up the start and end matches.

    Args:
        rounds_df: DataFrame with round data
        season: IPL season

    Returns:
        pd.DataFrame: Rounds data with start and end timestamps
    """
    logger.info("Adding match timestamps to rounds")

    if rounds_df.empty:
        return pd.DataFrame()

    try:
        async with get_db_session() as session:
            # Create a copy of rounds_df to avoid modifying the original
            rounds_with_dates = rounds_df.copy()

            # Process each round
            for i, row in rounds_with_dates.iterrows():
                first_match_num = row["first_match"]  # First match in round (inclusive)
                last_match_num = row["last_match"]  # Last match in round (inclusive)

                # Get start match date
                start_query = select(IPLMatch).where(
                    (IPLMatch.season == int(season))
                    & (IPLMatch.match_number == first_match_num)
                )
                start_result = await session.execute(start_query)
                start_match = start_result.scalar_one_or_none()

                # Get end match date
                end_query = select(IPLMatch).where(
                    (IPLMatch.season == int(season))
                    & (IPLMatch.match_number == last_match_num)
                )
                end_result = await session.execute(end_query)
                end_match = end_result.scalar_one_or_none()

                # Store timestamps if matches found
                if start_match:
                    # Ensure date has timezone info
                    date_utc = start_match.date_utc
                    if date_utc.tzinfo is None:
                        date_utc = date_utc.replace(tzinfo=timezone.utc)
                    rounds_with_dates.at[i, "start_date_utc"] = date_utc

                if end_match:
                    # Ensure date has timezone info
                    date_utc = end_match.date_utc
                    if date_utc.tzinfo is None:
                        date_utc = date_utc.replace(tzinfo=timezone.utc)
                    rounds_with_dates.at[i, "end_date_utc"] = date_utc

                # Calculate days in round if both dates available
                if start_match and end_match:
                    # Ensure both datetimes have timezone info for accurate calculation
                    start_date = start_match.date_utc
                    end_date = end_match.date_utc
                    if start_date.tzinfo is None:
                        start_date = start_date.replace(tzinfo=timezone.utc)
                    if end_date.tzinfo is None:
                        end_date = end_date.replace(tzinfo=timezone.utc)
                    days_diff = (end_date - start_date).days + 1
                    rounds_with_dates.at[i, "days_in_round"] = days_diff

            return rounds_with_dates

    except Exception as e:
        logger.error(f"Error adding timestamps to rounds: {e}")
        logger.error(traceback.format_exc())
        return rounds_df  # Return original if there's an error


async def store_balanced_rounds(rounds_df: pd.DataFrame, season: str = "2025") -> bool:
    """
    Store the calculated balanced rounds in the database.

    Args:
        rounds_df: DataFrame with round data
        season: IPL season

    Returns:
        bool: Success status
    """
    logger.info(f"Storing {len(rounds_df)} balanced rounds for season {season}")

    try:
        async with get_db_session() as session:
            season_int = int(season)

            # First clear all game_round_id references in matches for this season
            # This needs to happen before we can delete the rounds due to the foreign key constraint
            clear_refs_stmt = (
                sqlalchemy.update(IPLMatch)
                .where(IPLMatch.season == season_int)
                .values(game_round_id=None)
            )

            await session.execute(clear_refs_stmt)
            await session.commit()
            logger.info(f"Cleared game round references for season {season}")

            # Now we can safely delete the rounds
            delete_stmt = sqlalchemy.delete(IPLRound).where(
                IPLRound.season == season_int
            )
            await session.execute(delete_stmt)
            await session.commit()
            logger.info(f"Deleted existing rounds for season {season}")

            # Now create new rounds
            for _, row in rounds_df.iterrows():
                # Create round object with the new team_matches JSON field
                round_obj = IPLRound(
                    round_number=int(row["round_number"]),
                    season=season_int,
                    # Use first_match and last_match instead of start_match and end_match
                    first_match=int(row["first_match"]),
                    last_match=int(row["last_match"]),
                    matches_in_round=int(row["matches_in_round"]),
                    min_team_matches=int(row["min_team_matches"]),
                    max_team_matches=int(row["max_team_matches"]),
                    is_balanced=bool(row["is_balanced"]),
                    # Use the team_matches dictionary
                    team_matches=row.get("team_matches", {}),
                    # Date information from actual matches
                    start_date_utc=row.get("start_date_utc"),
                    end_date_utc=row.get("end_date_utc"),
                    days_in_round=(
                        int(row.get("days_in_round", 0))
                        if pd.notna(row.get("days_in_round"))
                        else None
                    ),
                )
                session.add(round_obj)

            await session.commit()
            logger.info(f"Successfully stored {len(rounds_df)} balanced rounds")
            return True

    except Exception as e:
        logger.error(f"Error storing balanced rounds: {e}")
        logger.error(traceback.format_exc())
        return False


async def update_matches_with_game_rounds(season: str = "2025") -> bool:
    """
    Update the game_round_id field on all matches based on the round boundaries.

    Args:
        season: IPL season

    Returns:
        bool: Success status
    """
    logger.info(f"Updating match game round IDs for season {season}")

    try:
        async with get_db_session() as session:
            # Get all rounds for this season
            rounds_query = (
                select(IPLRound)
                .where(IPLRound.season == int(season))
                .order_by(IPLRound.round_number)
            )

            result = await session.execute(rounds_query)
            rounds = result.scalars().all()

            if not rounds:
                logger.warning("No rounds found to update matches")
                return False

            # Update each match with its game round
            for round_obj in rounds:
                # Find matches in this round's range (using inclusive first_match and last_match)
                matches_query = select(IPLMatch).where(
                    and_(
                        IPLMatch.season == int(season),
                        IPLMatch.match_number
                        >= round_obj.first_match,  # GREATER THAN OR EQUAL
                        IPLMatch.match_number
                        <= round_obj.last_match,  # LESS THAN OR EQUAL
                    )
                )

                matches_result = await session.execute(matches_query)
                matches = matches_result.scalars().all()

                # Update each match
                for match in matches:
                    match.game_round_id = round_obj.id

            await session.commit()
            logger.info("Successfully updated match game round IDs")
            return True

    except Exception as e:
        logger.error(f"Error updating match game round IDs: {e}")
        logger.error(traceback.format_exc())
        return False


async def pipeline():
    """Run the complete pipeline to import fixtures and create balanced rounds for all seasons"""
    logger.info("Starting IPL fixtures import pipeline")

    seasons = ["2025"]  # Add more seasons if needed
    success = True

    for season in seasons:
        # Step 1: Import fixtures
        import_result = await import_fixtures(season)
        if not import_result:
            success = False
            logger.error(f"Failed to import fixtures for season {season}")
            continue

        # Step 2: Create balanced rounds
        rounds_result = await create_balanced_rounds(season)
        if not rounds_result:
            success = False
            logger.error(f"Failed to create balanced rounds for season {season}")
        else:
            logger.info(f"Successfully created balanced rounds for season {season}")

    if success:
        logger.info("Pipeline completed successfully")
    else:
        logger.warning("Pipeline completed with some errors")

    return success


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(pipeline())
