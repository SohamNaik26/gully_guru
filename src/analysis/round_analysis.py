import pandas as pd
import sqlalchemy
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

db_url = os.getenv("DATABASE_URL")


def get_sql(file_name: str) -> str:
    """
    Read SQL query from a file in the src/sql directory.

    Args:
        file_name (str): Name of the SQL file without extension

    Returns:
        str: Contents of the SQL file
    """
    with open(f"src/sql/{file_name}.sql", "r") as file:
        return file.read()


def get_data_from_db(query: str) -> pd.DataFrame:
    """
    Execute a SQL query against the database and return results as a DataFrame.

    Args:
        query (str): SQL query to execute

    Returns:
        pd.DataFrame: Results of the query
    """
    engine = sqlalchemy.create_engine(db_url)
    return pd.read_sql_query(query, engine)


def visualize_heatmap(df: pd.DataFrame) -> None:
    """
    Create and display a heatmap visualization showing the number of matches
    played by each team in each round.

    The heatmap uses color intensity to show where teams play more or fewer matches,
    making it easy to identify imbalances in the schedule.

    Args:
        df (pd.DataFrame): DataFrame with round_number, team, and matches_played columns
    """
    # Melt to long-form
    df_long = df.melt(
        id_vars="round_number", var_name="team", value_name="matches_played"
    )

    # Visualize with heatmap (based on rank)
    fig = px.density_heatmap(
        df_long,
        x="round_number",
        y="team",
        z="matches_played",
        color_continuous_scale="",
        title="Matches Played per Team in Each Round",
        labels={"round_number": "Round", "matches_played": "Matches Played"},
    )

    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis=dict(title="Team", autorange="reversed"),
        coloraxis_colorbar=dict(title="Matches"),
        template="plotly_white",
    )

    fig.show()


def evalutate_the_optimal_score_to_match_number(
    df: pd.DataFrame, off_by_match: int = 1, spacing: int = 7
) -> pd.DataFrame:
    """
    Evaluate optimal match numbers to use as round boundaries, ensuring:
    1. Teams have played a similar number of matches (within off_by_match tolerance)
    2. Selected match numbers are well distributed throughout the tournament

    Args:
        df (pd.DataFrame): DataFrame with team, match_number, and cumulative_matches_played
        off_by_match (int): Tolerance for match count differences (default: 1)
        spacing (int): Ideal spacing between selected match numbers (default: 7)

    Returns:
        pd.DataFrame: Well-distributed match numbers that make good round boundaries
    """
    # Convert cumulative_matches_played to numeric if it's not already
    df["cumulative_matches_played"] = pd.to_numeric(df["cumulative_matches_played"])

    # Group by match_number and calculate statistics
    match_stats = df.groupby("match_number").agg(
        {"cumulative_matches_played": ["min", "max", "mean", "std"]}
    )

    # Flatten the multi-index columns
    match_stats.columns = ["min_matches", "max_matches", "avg_matches", "std_matches"]

    # Calculate balance metrics:
    # 1. Range of matches played (lower is better)
    match_stats["range"] = match_stats["max_matches"] - match_stats["min_matches"]

    # 2. Is the range within our tolerance?
    match_stats["within_tolerance"] = match_stats["range"] <= off_by_match

    # 3. Coefficient of variation (std/mean) - normalized measure of dispersion
    match_stats["cv"] = match_stats["std_matches"] / match_stats["avg_matches"].replace(
        0, 1e-10
    )

    # 4. Combined score with bonuses for being within tolerance
    match_stats["balance_score"] = (0.7 * match_stats["range"]) + (
        0.3 * match_stats["cv"]
    )
    # Apply a significant bonus to matches within tolerance
    match_stats.loc[match_stats["within_tolerance"], "balance_score"] *= 0.5

    # Find matches with enough data (at least certain number of matches played)
    valid_matches = match_stats[match_stats["avg_matches"] >= 1].copy()

    # Add team count and total match information
    team_counts = df.groupby("match_number")["team"].nunique().reset_index()
    total_matches_by_number = (
        df.groupby("match_number")["cumulative_matches_played"].sum().reset_index()
    )

    # Sort all matches by match_number for sequential processing
    all_matches = valid_matches.reset_index().sort_values("match_number")
    all_matches = all_matches.merge(team_counts, on="match_number")
    all_matches = all_matches.merge(
        total_matches_by_number, on="match_number", suffixes=("", "_total")
    )

    # Select well-distributed match numbers
    selected_matches = []
    max_match = all_matches["match_number"].max()

    # First, get a set of candidate matches that are within tolerance
    candidates = all_matches[all_matches["within_tolerance"]].copy()

    # If we have too few candidates, relax the tolerance
    if len(candidates) < 5:
        # Use all matches but prioritize those with smaller ranges
        candidates = all_matches.copy()

    # Sort candidates by balance score (better scores first)
    candidates = candidates.sort_values("balance_score")

    # First match number as anchor point (using the best scoring early match)
    early_matches = candidates[candidates["match_number"] <= 15]
    if len(early_matches) > 0:
        selected_matches.append(early_matches.iloc[0]["match_number"])
    else:
        # Fall back to first available good match
        selected_matches.append(candidates.iloc[0]["match_number"])

    # Select remaining matches with good spacing
    while True:
        last_selected = selected_matches[-1]
        target_range = (last_selected + spacing - 2, last_selected + spacing + 2)

        # Find matches in the target range
        in_range = candidates[
            (candidates["match_number"] > target_range[0])
            & (candidates["match_number"] <= target_range[1])
        ]

        if len(in_range) > 0:
            # Select best match in range
            selected_matches.append(in_range.iloc[0]["match_number"])
        else:
            # Try with a wider range
            wider_range = (last_selected + spacing - 4, last_selected + spacing + 4)
            in_wider_range = candidates[
                (candidates["match_number"] > wider_range[0])
                & (candidates["match_number"] <= wider_range[1])
            ]

            if len(in_wider_range) > 0:
                selected_matches.append(in_wider_range.iloc[0]["match_number"])
            else:
                # Take the next best available match that's at least 3 matches away
                next_matches = candidates[
                    candidates["match_number"] > last_selected + 3
                ]
                if len(next_matches) > 0:
                    selected_matches.append(next_matches.iloc[0]["match_number"])
                else:
                    # No more suitable matches
                    break

        # Stop if we're getting too close to the end
        if selected_matches[-1] >= max_match - 5:
            break

        # Avoid too many rounds
        if len(selected_matches) >= 10:
            break

    # Get detailed data for the selected matches
    selected_data = all_matches[
        all_matches["match_number"].isin(selected_matches)
    ].copy()
    selected_data = selected_data.sort_values("match_number")

    # Format the results
    result = selected_data[
        [
            "match_number",
            "min_matches",
            "max_matches",
            "avg_matches",
            "range",
            "within_tolerance",
            "balance_score",
            "team",
            "cumulative_matches_played",
        ]
    ]

    result = result.rename(
        columns={
            "team": "team_count",
            "cumulative_matches_played": "total_matches_played",
        }
    )

    print(f"Selected {len(result)} match numbers as optimal round boundaries:")
    for i, row in result.iterrows():
        tolerance_text = "✓" if row["within_tolerance"] else "✗"
        print(
            f"Match #{row['match_number']}: Range {row['range']:.1f} {tolerance_text}, "
            f"Min {row['min_matches']:.1f}, Max {row['max_matches']:.1f}, "
            f"Avg {row['avg_matches']:.1f}, Score {row['balance_score']:.3f}"
        )

    # Also print spacing between selected match numbers
    if len(selected_matches) > 1:
        print("\nSpacing between selected matches:")
        for i in range(1, len(selected_matches)):
            gap = selected_matches[i] - selected_matches[i - 1]
            print(
                f"Between match #{selected_matches[i-1]} and #{selected_matches[i]}: {gap} matches"
            )

    # Calculate average of team matches per round
    if len(selected_matches) > 1:
        print("\nMatches per team per round:")
        selected_matches = [0] + selected_matches  # Add 0 as starting point

        for i in range(1, len(selected_matches)):
            start_match = selected_matches[i - 1]
            end_match = selected_matches[i]

            # For each team, find match count difference
            team_counts = {}
            for team in df["team"].unique():
                team_df = df[df["team"] == team]

                # Get start and end counts
                start_count = 0
                if start_match > 0:
                    start_rows = team_df[team_df["match_number"] == start_match]
                    if not start_rows.empty:
                        start_count = start_rows["cumulative_matches_played"].values[0]

                end_rows = team_df[team_df["match_number"] == end_match]
                end_count = 0
                if not end_rows.empty:
                    end_count = end_rows["cumulative_matches_played"].values[0]

                team_counts[team] = end_count - start_count

            # Print summary for this round
            round_number = i
            min_count = min(team_counts.values()) if team_counts else 0
            max_count = max(team_counts.values()) if team_counts else 0
            avg_count = (
                sum(team_counts.values()) / len(team_counts) if team_counts else 0
            )
            print(
                f"Round {round_number} (Match #{start_match+1}-{end_match}): "
                f"Min={min_count:.1f}, Max={max_count:.1f}, Avg={avg_count:.1f}"
            )

    return result


def alt_evalutate_the_optimal_score_to_match_number(
    df: pd.DataFrame, top_k: int = 10, off_by_match: int = 1
) -> pd.DataFrame:
    """
    Alternative approach to find optimal match numbers for round boundaries.

    This function uses mean absolute deviation and standard deviation to identify
    match numbers where teams have played a similar number of matches, then ensures
    the selected match numbers are well-distributed across the tournament.

    Args:
        df (pd.DataFrame): DataFrame with team, match_number, and cumulative_matches_played
        top_k (int): Number of match numbers to select
        off_by_match (int): Minimum spacing between selected match numbers

    Returns:
        pd.DataFrame: Selected match numbers with their balance metrics
    """
    df["cumulative_matches_played"] = pd.to_numeric(df["cumulative_matches_played"])
    df["match_number"] = pd.to_numeric(df["match_number"])

    # Aggregate match-wise balance metric (mean absolute deviation)
    match_scores = (
        df.groupby("match_number")["cumulative_matches_played"]
        .agg(
            std_dev="std",
            mean_abs_diff=lambda x: (x - x.mean()).abs().mean(),
            max_minus_min=lambda x: x.max() - x.min(),
        )
        .reset_index()
        .sort_values("mean_abs_diff")
        .reset_index(drop=True)
    )

    # Select top_k match numbers spaced out by `off_by_match`
    selected = []
    used_matches = set()

    for _, row in match_scores.iterrows():
        m = row["match_number"]
        if all(abs(m - s) > off_by_match for s in used_matches):
            selected.append(row)
            used_matches.add(m)
        if len(selected) >= top_k:
            break

    result = pd.DataFrame(selected)

    print(f"Top {top_k} distributed match numbers with tolerance ±{off_by_match}:")
    print(result)

    return result


def visualize_match_optimization(
    df: pd.DataFrame, selected_matches: list, match_stats: pd.DataFrame = None
) -> None:
    """
    Visualize the optimization of match numbers for round boundaries through multiple plots.

    This function creates several visualizations to help understand the optimization process:
    1. Balance metrics across all match numbers
    2. Team match counts at each selected boundary
    3. Match distribution across teams in each proposed round

    Args:
        df (pd.DataFrame): DataFrame with team, match_number, and cumulative_matches_played
        selected_matches (list): Match numbers selected as optimal round boundaries
        match_stats (pd.DataFrame, optional): DataFrame with match statistics if already computed
    """
    # If match_stats not provided, compute it
    if match_stats is None:
        df["cumulative_matches_played"] = pd.to_numeric(df["cumulative_matches_played"])
        match_stats = df.groupby("match_number").agg(
            {"cumulative_matches_played": ["min", "max", "mean", "std"]}
        )
        match_stats.columns = [
            "min_matches",
            "max_matches",
            "avg_matches",
            "std_matches",
        ]
        match_stats["range"] = match_stats["max_matches"] - match_stats["min_matches"]
        match_stats["within_tolerance"] = match_stats["range"] <= 1
        match_stats["cv"] = match_stats["std_matches"] / match_stats[
            "avg_matches"
        ].replace(0, 1e-10)
        match_stats["balance_score"] = (0.7 * match_stats["range"]) + (
            0.3 * match_stats["cv"]
        )
        match_stats.loc[match_stats["within_tolerance"], "balance_score"] *= 0.5

    # Reset index to make match_number a column
    match_stats = match_stats.reset_index()

    # 1. FIRST VISUALIZATION: Match balance metrics
    # Create figure with secondary y-axis
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])

    # Add range (max-min) as bars
    fig1.add_trace(
        go.Bar(
            x=match_stats["match_number"],
            y=match_stats["range"],
            name="Range (Max-Min)",
            marker_color="lightblue",
            opacity=0.7,
        ),
        secondary_y=False,
    )

    # Add balance score as line
    fig1.add_trace(
        go.Scatter(
            x=match_stats["match_number"],
            y=match_stats["balance_score"],
            name="Balance Score",
            line=dict(color="red", width=2),
        ),
        secondary_y=True,
    )

    # Add vertical lines for selected match numbers
    for match in selected_matches:
        fig1.add_vline(
            x=match,
            line_width=2,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Match {match}",
            annotation_position="top right",
        )

    # Update layout
    fig1.update_layout(
        title_text="Match Balance Metrics Across Tournament",
        xaxis_title="Match Number",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    fig1.update_yaxes(title_text="Range (Max-Min Matches)", secondary_y=False)
    fig1.update_yaxes(title_text="Balance Score (lower is better)", secondary_y=True)

    # 2. SECOND VISUALIZATION: Team match counts at boundaries
    # Prepare data for cumulative matches by team
    pivot_data = df.pivot(
        index="match_number", columns="team", values="cumulative_matches_played"
    )

    # Create figure for team progress
    fig2 = go.Figure()

    # Add a line for each team
    for team in pivot_data.columns:
        fig2.add_trace(
            go.Scatter(x=pivot_data.index, y=pivot_data[team], mode="lines", name=team)
        )

    # Add vertical lines for selected match numbers
    for match in selected_matches:
        fig2.add_vline(
            x=match,
            line_width=2,
            line_dash="dash",
            line_color="black",
            annotation_text=f"Round End",
            annotation_position="top right",
        )

    # Update layout
    fig2.update_layout(
        title_text="Cumulative Matches Played by Each Team",
        xaxis_title="Match Number",
        yaxis_title="Matches Played",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
    )

    # 3. THIRD VISUALIZATION: Rounds balance heatmap
    # Calculate matches per team per round
    selected_matches_with_zero = [0] + selected_matches
    round_data = []

    for i in range(1, len(selected_matches_with_zero)):
        start_match = selected_matches_with_zero[i - 1]
        end_match = selected_matches_with_zero[i]

        for team in df["team"].unique():
            team_df = df[df["team"] == team]

            # Get start and end counts
            start_count = 0
            if start_match > 0:
                start_rows = team_df[team_df["match_number"] == start_match]
                if not start_rows.empty:
                    start_count = start_rows["cumulative_matches_played"].values[0]

            end_rows = team_df[team_df["match_number"] == end_match]
            end_count = 0
            if not end_rows.empty:
                end_count = end_rows["cumulative_matches_played"].values[0]

            round_matches = end_count - start_count
            round_data.append(
                {"Round": f"Round {i}", "Team": team, "Matches": round_matches}
            )

    # Create DataFrame from round data
    round_df = pd.DataFrame(round_data)

    # Create heatmap
    fig3 = px.density_heatmap(
        round_df,
        x="Round",
        y="Team",
        z="Matches",
        color_continuous_scale="Viridis",
        title="Matches per Team in Each Proposed Round",
    )

    fig3.update_layout(
        yaxis=dict(autorange="reversed"), coloraxis_colorbar=dict(title="Matches")
    )

    # Display all figures
    fig1.show()
    fig2.show()
    fig3.show()

    # 4. BONUS: Statistical summary of rounds
    round_stats = round_df.groupby("Round")["Matches"].agg(
        ["min", "max", "mean", "std"]
    )
    round_stats["range"] = round_stats["max"] - round_stats["min"]
    round_stats["cv"] = round_stats["std"] / round_stats["mean"]

    # Create a figure for round statistics
    fig4 = go.Figure()

    fig4.add_trace(
        go.Bar(
            x=round_stats.index,
            y=round_stats["range"],
            name="Range (Max-Min)",
            marker_color="lightblue",
        )
    )

    fig4.add_trace(
        go.Scatter(
            x=round_stats.index,
            y=round_stats["mean"],
            name="Average Matches",
            mode="markers+lines",
            marker=dict(size=10),
            line=dict(width=2, color="darkgreen"),
        )
    )

    # Add error bars to show min/max
    for i, (idx, row) in enumerate(round_stats.iterrows()):
        fig4.add_shape(
            type="line",
            x0=i,
            y0=row["min"],
            x1=i,
            y1=row["max"],
            line=dict(color="gray", width=2),
        )

    fig4.update_layout(
        title_text="Statistics for Each Proposed Round",
        xaxis_title="Round",
        yaxis_title="Matches",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )

    fig4.show()


def create_rounds_summary_table(
    df: pd.DataFrame, selected_matches: list
) -> pd.DataFrame:
    """
    Create a comprehensive summary table of all rounds with key metrics and team-specific data.

    Args:
        df (pd.DataFrame): DataFrame with team, match_number, and cumulative_matches_played
        selected_matches (list): Match numbers selected as optimal round boundaries

    Returns:
        pd.DataFrame: A summary table with all round metrics and team-specific match counts
    """
    # Ensure data is numeric
    df["cumulative_matches_played"] = pd.to_numeric(df["cumulative_matches_played"])

    # Prepare rounds data
    selected_matches_with_zero = [0] + selected_matches
    rounds_data = []
    teams = sorted(df["team"].unique())

    for i in range(1, len(selected_matches_with_zero)):
        start_match = selected_matches_with_zero[i - 1]
        end_match = selected_matches_with_zero[i]

        # Initial round data with identifiers
        round_data = {
            "round_number": i,
            "start_match": start_match
            + 1,  # Add 1 since we want matches after the boundary
            "end_match": end_match,
            "matches_in_round": end_match - start_match,
        }

        # Calculate team-specific metrics
        team_matches = {}
        all_team_matches = []

        for team in teams:
            team_df = df[df["team"] == team]

            # Get start and end counts
            start_count = 0
            if start_match > 0:
                start_rows = team_df[team_df["match_number"] == start_match]
                if not start_rows.empty:
                    start_count = start_rows["cumulative_matches_played"].values[0]

            end_rows = team_df[team_df["match_number"] == end_match]
            end_count = 0
            if not end_rows.empty:
                end_count = end_rows["cumulative_matches_played"].values[0]

            # Calculate matches in this round for this team
            matches_in_round = end_count - start_count
            team_matches[team] = matches_in_round
            all_team_matches.append(matches_in_round)

            # Add to round data
            round_data[f"{team}_matches"] = matches_in_round

        # Add overall round statistics
        if all_team_matches:
            round_data["min_team_matches"] = min(all_team_matches)
            round_data["max_team_matches"] = max(all_team_matches)
            round_data["avg_team_matches"] = sum(all_team_matches) / len(
                all_team_matches
            )
            round_data["std_team_matches"] = pd.Series(all_team_matches).std()
            round_data["range_team_matches"] = (
                round_data["max_team_matches"] - round_data["min_team_matches"]
            )
            round_data["balanced"] = (
                round_data["min_team_matches"] == round_data["max_team_matches"]
            )

        # Add date range information if available in the dataframe
        if "date_utc" in df.columns:
            # For each match in this round range, get min and max dates
            round_matches = df[
                (df["match_number"] > start_match) & (df["match_number"] <= end_match)
            ]
            if not round_matches.empty:
                unique_matches = round_matches.drop_duplicates("match_number")
                round_data["start_date"] = unique_matches["date_utc"].min()
                round_data["end_date"] = unique_matches["date_utc"].max()
                round_data["days_in_round"] = (
                    round_data["end_date"] - round_data["start_date"]
                ).days + 1

        rounds_data.append(round_data)

    # Create DataFrame from the collected data
    rounds_df = pd.DataFrame(rounds_data)

    # Reorder columns for better readability
    metric_cols = [
        "round_number",
        "start_match",
        "end_match",
        "matches_in_round",
        "min_team_matches",
        "max_team_matches",
        "avg_team_matches",
        "range_team_matches",
        "std_team_matches",
        "balanced",
    ]

    # Add date columns if they exist
    if "start_date" in rounds_df.columns:
        metric_cols.extend(["start_date", "end_date", "days_in_round"])

    # Add team-specific columns
    team_cols = [f"{team}_matches" for team in teams]

    # Combine column orders
    col_order = metric_cols + team_cols

    # Reorder columns, only including those that exist
    existing_cols = [col for col in col_order if col in rounds_df.columns]
    rounds_df = rounds_df[existing_cols]

    # Format the numerical columns
    for col in rounds_df.columns:
        if col.endswith("_matches") or col in ["avg_team_matches", "std_team_matches"]:
            rounds_df[col] = rounds_df[col].round(1)

    return rounds_df


def display_rounds_summary(rounds_df: pd.DataFrame) -> None:
    """
    Display the rounds summary table in a visually appealing way with color coding.

    Args:
        rounds_df (pd.DataFrame): The rounds summary DataFrame from create_rounds_summary_table
    """
    # Create a styled version of the dataframe
    styled_df = rounds_df.style

    # Add color scale for balance metrics (greener is better)
    balance_cols = ["range_team_matches", "std_team_matches"]
    for col in balance_cols:
        if col in rounds_df.columns:
            styled_df = styled_df.background_gradient(
                cmap="RdYlGn_r", subset=[col], vmin=0, vmax=2
            )

    # Highlight balanced rounds
    if "balanced" in rounds_df.columns:
        styled_df = styled_df.applymap(
            lambda x: "background-color: #c6efce; color: #006100" if x else "",
            subset=["balanced"],
        )

    # Add better formatting for dates if they exist
    date_cols = ["start_date", "end_date"]
    for col in date_cols:
        if col in rounds_df.columns:
            styled_df = styled_df.format({col: lambda x: x.strftime("%Y-%m-%d")})

    # Display the styled table
    print(styled_df)

    # Also print some key summary statistics
    print(f"\nRound Balance Summary:")
    print(f"- Number of rounds: {len(rounds_df)}")

    if "balanced" in rounds_df.columns:
        balanced_count = rounds_df["balanced"].sum()
        print(
            f"- Perfectly balanced rounds: {balanced_count} ({balanced_count/len(rounds_df)*100:.1f}%)"
        )

    if "range_team_matches" in rounds_df.columns:
        avg_range = rounds_df["range_team_matches"].mean()
        print(f"- Average match imbalance (range): {avg_range:.2f} matches")


if __name__ == "__main__":
    # -----------------------------
    # Data
    # ----------------------------

    query_ipl_teams_match_played_count_by_match_number = get_sql(
        "ipl_teams_match_played_count_by_match_number"
    )
    df_ipl_teams_match_played_count_by_match_number = get_data_from_db(
        query_ipl_teams_match_played_count_by_match_number
    )

    print("Create rounds summary table")
    rounds_df = create_rounds_summary_table(
        df_ipl_teams_match_played_count_by_match_number,
        evalutate_the_optimal_score_to_match_number(
        df_ipl_teams_match_played_count_by_match_number
        )["match_number"].tolist(),
    )

    print("Display rounds summary")
    display_rounds_summary(rounds_df)

    rounds_df.to_csv("data/effective_rounds_summary.csv", index=False)
