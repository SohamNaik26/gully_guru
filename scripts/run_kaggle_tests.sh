#!/bin/bash
# Script to run Kaggle integration tests

# Set up colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Kaggle Integration Tests${NC}"
echo "=================================="

# Check if we should run with pytest or manually
if [ "$1" == "--manual" ]; then
    echo -e "${YELLOW}Running tests manually (without pytest)${NC}"
    pipenv run python tests/integrations/test_kaggle.py
else
    echo -e "${YELLOW}Running tests with pytest${NC}"
    pipenv run pytest -v tests/integrations/test_kaggle.py
fi

# Check the exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All Kaggle integration tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some Kaggle integration tests failed!${NC}"
    exit 1
fi 