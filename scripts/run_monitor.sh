#!/bin/bash
# Run the database monitor script

# Set environment variables
export API_URL="http://localhost:8000"
export CHECK_INTERVAL=60
export MAX_FAILURES=3
export API_RESTART_COMMAND="bash $(pwd)/scripts/run_api.sh"
export BOT_RESTART_COMMAND="bash $(pwd)/scripts/run_bot.sh"

# Activate virtual environment if using one
# source .venv/bin/activate

# Run the monitor script
echo "Starting database monitor..."
python scripts/monitor_db.py 