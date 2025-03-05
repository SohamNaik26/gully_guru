import httpx
import pandas as pd


class CricsheetDataFactory:
    def __init__(self):
        self.base_url = "https://cricsheet.org/register/"

    def download_csv(self, file_name):
        url = f"{self.base_url}{file_name}"
        response = httpx.get(url)
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download {file_name}")

    def load_people_data(self):
        csv_content = self.download_csv("people.csv")
        df = pd.read_csv(pd.compat.StringIO(csv_content.decode("utf-8")))
        return df
