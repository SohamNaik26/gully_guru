import os
import pandas as pd
import pandas_gbq
from jinja2 import Template


def get_raw_from_bq(sql_file_name) -> pd.DataFrame:

    with open(f"yolo/sql/{sql_file_name}.sql", "r") as file:
        sql = file.read()

    return pandas_gbq.read_gbq(sql)


def read_sql_from_file_add_template(sql_file_name, template_data: dict) -> str:
    """
    Get SQL query from SQL file and apply Jinja2 templating.
    input:
        sql_file_name: str
        template_data: dict
    output:
        str
    """
    try:
        sql_dir = os.path.join("yolo", "sql", f"{sql_file_name}.sql")

        with open(sql_dir, "r") as sql_file:
            file_content = sql_file.read()
            query = Template(file_content).render(template_data)
            return query

    except FileNotFoundError:
        print(f"The file {sql_dir} was not found.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
