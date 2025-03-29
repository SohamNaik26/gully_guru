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


def get_participant_player_data() -> pd.DataFrame:
    sql = """
            SELECT 
                gp.team_name AS team_name,
                ROUND(gp.budget, 2) AS team_budget_left,
                p.name AS player_name,
                p.team AS player_ipl_team,
                p.player_type AS player_role,
                ROUND(pp.purchase_price, 2) AS player_price
            FROM participant_players pp
            LEFT JOIN players p ON p.id = pp.player_id
            LEFT JOIN gully_participants gp ON gp.id = pp.gully_participant_id
            WHERE gp.gully_id = 7;
        """
    return get_data_from_db(sql)


def players_in_auction_queue() -> pd.DataFrame:
    sql = """
        SELECT
            p.name AS player_name,
            p.team AS player_ipl_team,
            p.player_type AS player_role,
            p.base_price AS price,
            p.sold_price AS current_ipl_price
        FROM auction_queue aq
        LEFT JOIN players p ON p.id = aq.player_id
        WHERE aq.gully_id = 7
        AND aq.status = 'pending'
        ORDER BY p.team, p.sold_price DESC;
        """
    return get_data_from_db(sql)


if __name__ == "__main__":
    current_team = get_participant_player_data()
    print(current_team)
    current_team.to_csv("data/current_team.csv", index=False)
    que_df = players_in_auction_queue()
    que_df.to_csv("data/que_df.csv", index=False)
