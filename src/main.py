import uvicorn
import logging
from src.app import app  # Changed back to absolute import for running from root

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
