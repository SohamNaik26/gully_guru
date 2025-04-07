#!/bin/bash

# Run Frontend script for GullyGuru
# This script runs the React frontend service

# Set up colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GullyGuru Frontend service...${NC}"

# Function to handle cleanup on exit
cleanup() {
    echo -e "${RED}Stopping Frontend service...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up trap for cleanup on script termination
trap cleanup SIGINT SIGTERM

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed. Please install it first.${NC}"
    exit 1
fi

# Ensure we're in the project root directory
cd "$(dirname "$0")/.." || exit 1

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: 'frontend' directory not found.${NC}"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    echo -e "${BLUE}Loading environment variables from .env file...${NC}"
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Warning: .env file not found. Make sure environment variables are set.${NC}"
fi

# Kill any existing processes using port 3000
echo -e "${BLUE}Checking for processes using port 3000...${NC}"
if command -v lsof &> /dev/null; then
    PORT_PID=$(lsof -ti:3000)
    if [ -n "$PORT_PID" ]; then
        echo -e "${BLUE}Killing process $PORT_PID using port 3000...${NC}"
        kill -9 $PORT_PID 2>/dev/null
        sleep 1
    fi
fi

# Navigate to frontend directory
cd frontend || exit 1

# Check if node_modules exists, if not, install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing dependencies...${NC}"
    npm install
fi

# Start the frontend
echo -e "${BLUE}Starting React development server...${NC}"
npm start &
FRONTEND_PID=$!

echo -e "${GREEN}Frontend service is running at http://localhost:3000${NC}"
echo -e "${GREEN}Press Ctrl+C to stop the service.${NC}"

# Wait for background process
wait 