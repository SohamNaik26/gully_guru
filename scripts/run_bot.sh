#!/bin/bash

# Run Bot script for GullyGuru
# This script runs the Telegram bot service

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GullyGuru Bot service...${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "${RED}Stopping Bot service...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up trap for cleanup on script termination
trap cleanup SIGINT SIGTERM

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo -e "${RED}Error: pipenv is not installed. Please install it first.${NC}"
    exit 1
fi

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit 1

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Warning: .env file not found. Make sure environment variables are set.${NC}"
fi

# Kill any existing bot processes
echo -e "${BLUE}Killing any existing bot processes...${NC}"
pkill -f "python -m src.bot.bot" 2>/dev/null
sleep 1

# Start the Telegram bot
echo -e "${BLUE}Starting Telegram bot...${NC}"
pipenv run python -m src.bot.bot &
BOT_PID=$!
echo -e "${GREEN}Telegram bot started with PID: $BOT_PID${NC}"

# Check if the bot is actually running after a few seconds
sleep 3
if ! ps -p $BOT_PID > /dev/null; then
    echo -e "${RED}Bot process failed to start or exited quickly. Check logs for errors.${NC}"
    # Try to run it directly to see the output
    echo -e "${BLUE}Attempting to start bot directly...${NC}"
    pipenv run python -m src.bot.bot &
    BOT_PID=$!
    echo -e "${GREEN}Telegram bot restarted with PID: $BOT_PID${NC}"
fi

echo -e "${GREEN}Bot service is running. Press Ctrl+C to stop the service.${NC}"

# Wait for all background processes to finish
wait 