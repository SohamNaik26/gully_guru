from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from decimal import Decimal

import kagglehub
import csv
import pandas as pd
from sqlmodel import Session

from src.models.kaggle import Player
from src.db.models import Player
from src.db.session import get_session


def download_ipl_2025_mega_auction_dataset() -> Optional[Path]:
    """
    Download the IPL 2025 mega auction dataset.

    Returns:
        Path to the downloaded dataset or None if download fails
    """
    dataset_id = "souviksamanta1053/ipl-2025-mega-auction-dataset"
    try:
        path = kagglehub.dataset_download(dataset_id)
        print(f"Successfully downloaded IPL auction dataset")
        return Path(path)
    except Exception as e:
        print(f"Error downloading IPL auction dataset: {e}")
        return None


def download_kaggle_datasets(datasets: List[str]) -> Dict[str, Path]:
    """
    Download multiple Kaggle datasets and return their local paths.

    Args:
        datasets: List of Kaggle dataset identifiers (e.g., "username/dataset-name")

    Returns:
        Dictionary mapping dataset identifiers to their local paths
    """
    dataset_paths = {}
    for dataset in datasets:
        try:
            path = kagglehub.dataset_download(dataset)
            dataset_paths[dataset] = Path(path)
            print(f"Successfully downloaded dataset: {dataset}")
        except Exception as e:
            print(f"Error downloading dataset {dataset}: {e}")

    return dataset_paths


def get_all_datasets() -> Dict[str, Optional[Path]]:
    """
    Download all configured datasets.

    Returns:
        Dictionary containing all dataset paths
    """

    # Add individual dataset downloads here
    datasets_ipl_auction = download_ipl_2025_mega_auction_dataset()
    # lower case the keys for the datasets
    datasets_ipl_auction
    # add date of pull, created_at
    datasets_ipl_auction["created_at"] = datetime.now().isoformat()

    return datasets_ipl_auction


def load_kaggle_players_from_csv(file_path: str) -> List[KagglePlayer]:
    """
    Load player data from a Kaggle CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of KagglePlayer objects
    """
    try:
        # Read CSV using pandas for better handling of data types
        df = pd.read_csv(file_path)
        
        # Convert DataFrame to list of dictionaries
        players_data = df.to_dict(orient="records")
        
        # Validate and convert to KagglePlayer objects
        players = [KagglePlayer(**player_data) for player_data in players_data]
        
        return players
    except Exception as e:
        raise ValueError(f"Error loading Kaggle players from CSV: {str(e)}")


def import_kaggle_players_to_db(
    file_path: str, session: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Import players from Kaggle CSV to database.
    
    Args:
        file_path: Path to the CSV file
        session: Database session (optional)
        
    Returns:
        Dictionary with import results
    """
    close_session = False
    if session is None:
        session = next(get_session())
        close_session = True
    
    try:
        # Load players from CSV
        kaggle_players = load_kaggle_players_from_csv(file_path)
        
        # Convert to database models
        db_players = []
        for kp in kaggle_players:
            player_data = kp.to_db_model()
            db_player = Player(**player_data)
            db_players.append(db_player)
        
        # Bulk insert
        session.add_all(db_players)
        session.commit()
        
        # Return results
        return {
            "success": True,
            "imported_count": len(db_players),
            "players": db_players
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


if __name__ == "__main__":
    get_all_datasets()
