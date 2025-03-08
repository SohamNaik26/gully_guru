# GullyGuru Scripts

This directory contains utility scripts for the GullyGuru project.

## Available Scripts

### `run_services.sh`

Runs both the API server and Telegram bot simultaneously.

**Usage:**

```bash
./scripts/run_services.sh
```

**Features:**
- Starts both services from the project root directory
- Handles proper cleanup on exit (Ctrl+C)
- Loads environment variables from .env file
- Provides colored output for better readability

**Requirements:**
- pipenv must be installed
- .env file should be present in the project root with required environment variables

**Environment Variables:**
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `DATABASE_URL`: Database connection string
- `API_BASE_URL`: Base URL for the API (defaults to http://localhost:8000)

## Adding New Scripts

When adding new scripts to this directory:
1. Make them executable with `chmod +x scripts/your_script.sh`
2. Add documentation in this README
3. Follow the same error handling and output formatting patterns 