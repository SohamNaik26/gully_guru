#!/bin/bash
# Script to run GullyGuru tests

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running GullyGuru Tests${NC}"
echo "=================================="

# Check if a specific test was requested
if [ $# -eq 0 ]; then
    # No arguments, run all tests
    echo -e "${YELLOW}Running all tests${NC}"
    pipenv run pytest -v
else
    # Run specific tests
    echo -e "${YELLOW}Running specific tests: $1${NC}"
    pipenv run pytest -v "$@"
fi

# Check the exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi 