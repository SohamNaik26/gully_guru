import os
import sys
import uvicorn
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default environment variables for development if not present
if not os.environ.get("TELEGRAM_BOT_TOKEN"):
    print("⚠️ Warning: TELEGRAM_BOT_TOKEN not set, using dummy value for development")
    os.environ["TELEGRAM_BOT_TOKEN"] = "dummy_token_for_development"

if not os.environ.get("DATABASE_URL"):
    print("⚠️ Warning: DATABASE_URL not set, using local PostgreSQL for development")
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/fantasy_cricket"

# Check current working directory and update import path
if os.path.basename(os.getcwd()) == "src":
    # Running from src directory
    from app import app
else:
    # Running from project root
    from src.app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Start the FastAPI server
    # Database initialization happens in the app's lifespan
    uvicorn.run(app, host="0.0.0.0", port=8000)
