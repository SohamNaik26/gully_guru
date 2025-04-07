#!/bin/bash

# GullyGuru Frontend Runner
# This script starts the Next.js frontend application

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "  ____       _ _         ____                      "
echo " / ___|_   _| | |_   _  / ___|_   _ _ __ _   _     "
echo "| |  _| | | | | | | | | | |  _| | | | '__| | | |   "
echo "| |_| | |_| | | | |_| | | |_| | |_| | |  | |_| |   "
echo " \____|\__,_|_|_|\__, |  \____|\__,_|_|   \__,_|   "
echo "                 |___/   Frontend Runner           "
echo -e "${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for Node.js
if ! command_exists node; then
  echo -e "${RED}Error: Node.js is not installed.${NC}"
  echo "Please install Node.js from https://nodejs.org"
  exit 1
fi

# Check for npm
if ! command_exists npm; then
  echo -e "${RED}Error: npm is not installed.${NC}"
  echo "Please install npm, which usually comes with Node.js"
  exit 1
fi

# Check if we're in the project root
if [ ! -d "frontend" ]; then
  echo -e "${RED}Error: 'frontend' directory not found.${NC}"
  echo "Please run this script from the project root directory."
  exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if .env.local exists, create from example if not
if [ ! -f ".env.local" ]; then
  if [ -f ".env.local.example" ]; then
    echo -e "${YELLOW}Warning: .env.local not found. Creating from example file.${NC}"
    cp .env.local.example .env.local
    echo -e "${YELLOW}Please update .env.local with your actual configuration values.${NC}"
  else
    echo -e "${YELLOW}Warning: No .env files found. Creating a basic .env.local file.${NC}"
    cat > .env.local << EOL
# Authentication
NEXTAUTH_SECRET=development-secret
NEXTAUTH_URL=http://localhost:3000

# Google OAuth (add your credentials)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# API
NEXT_PUBLIC_API_URL=http://localhost:8000
EOL
    echo -e "${YELLOW}Created .env.local with placeholder values. Please update with your actual configuration.${NC}"
  fi
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing dependencies...${NC}"
  npm install
fi

# Run the development server
echo -e "${GREEN}Starting GullyGuru frontend on http://localhost:3000${NC}"
npm run dev 