#!/usr/bin/env python
"""
Database connection monitoring script.

This script periodically checks the health of the database connection
and restarts the application if the connection is unhealthy.
"""

import os
import time
import logging
import requests
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("db_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("db_monitor")

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
HEALTH_ENDPOINT = f"{API_URL}/health"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
MAX_FAILURES = int(os.getenv("MAX_FAILURES", "3"))
API_RESTART_COMMAND = os.getenv("API_RESTART_COMMAND", "bash scripts/run_api.sh")
BOT_RESTART_COMMAND = os.getenv("BOT_RESTART_COMMAND", "bash scripts/run_bot.sh")


def check_health():
    """
    Check the health of the API and database.

    Returns:
        bool: True if healthy, False otherwise
    """
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code != 200:
            logger.error(
                f"Health check failed with status code: {response.status_code}"
            )
            return False

        data = response.json()
        if data.get("database") != "healthy":
            logger.error(f"Database health check failed: {data}")
            return False

        logger.info("Health check passed")
        return True
    except requests.RequestException as e:
        logger.error(f"Health check request failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during health check: {e}")
        return False


def restart_services():
    """
    Restart the API and bot services.
    """
    try:
        logger.info("Restarting API service...")
        subprocess.run(API_RESTART_COMMAND, shell=True, check=True)
        logger.info("API service restarted successfully")

        logger.info("Restarting Bot service...")
        subprocess.run(BOT_RESTART_COMMAND, shell=True, check=True)
        logger.info("Bot service restarted successfully")

        # Wait for services to start up
        logger.info("Waiting for services to start up...")
        time.sleep(10)

        return True
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to restart services: {e}")
        return False


def main():
    """
    Main monitoring loop.
    """
    logger.info("Starting database connection monitor")

    failure_count = 0
    last_restart = None

    while True:
        try:
            if check_health():
                # Reset failure count on successful health check
                failure_count = 0
            else:
                failure_count += 1
                logger.warning(
                    f"Health check failed {failure_count}/{MAX_FAILURES} times"
                )

                # Restart services if max failures reached and not restarted recently
                if failure_count >= MAX_FAILURES:
                    current_time = datetime.now()

                    # Don't restart more than once per hour
                    if (
                        last_restart is None
                        or (current_time - last_restart).total_seconds() > 3600
                    ):
                        logger.warning("Maximum failures reached, restarting services")
                        if restart_services():
                            last_restart = current_time
                            failure_count = 0
                    else:
                        logger.warning(
                            "Services already restarted recently, skipping restart"
                        )

            # Sleep until next check
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
