import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add the current directory to Python's path
sys.path.append(os.path.abspath("."))

# Load environment variables
load_dotenv()

# Set default environment variables for development if not present
if not os.environ.get("TELEGRAM_BOT_TOKEN"):
    print("⚠️ Warning: TELEGRAM_BOT_TOKEN not set, using dummy value for development")
    os.environ["TELEGRAM_BOT_TOKEN"] = "dummy_token_for_development"

if not os.environ.get("DATABASE_URL"):
    print("⚠️ Warning: DATABASE_URL not set, using local PostgreSQL for development")
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/fantasy_cricket"

# Import the app from src
from src.app import app

if __name__ == "__main__":
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000) 