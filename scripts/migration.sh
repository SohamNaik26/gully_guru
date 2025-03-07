#!/bin/bash
# Database migration script for GullyGuru
# This script automates common migration tasks using Pipenv

set -e  # Exit on error

# Load environment variables
if [ -f .env ]; then
    echo "Loading .env environment variables..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set."
    echo "Please set it in your .env file or export it before running this script."
    exit 1
fi

# Function to display usage information
show_usage() {
    echo "GullyGuru Database Migration Script"
    echo ""
    echo "Usage: pipenv run ./scripts/migration.sh [command]"
    echo ""
    echo "Commands:"
    echo "  init           Initialize Alembic if not already initialized"
    echo "  create [msg]   Create a new migration with the given message"
    echo "  upgrade        Apply all pending migrations"
    echo "  downgrade [n]  Downgrade n migrations (default: 1)"
    echo "  reset          Reset the database (downgrade to base and upgrade to head)"
    echo "  history        Show migration history"
    echo "  current        Show current migration version"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  pipenv run ./scripts/migration.sh create 'Add user table'"
    echo "  pipenv run ./scripts/migration.sh upgrade"
    echo "  pipenv run ./scripts/migration.sh downgrade 2"
}

# Initialize Alembic if not already initialized
init_alembic() {
    if [ ! -d "alembic" ]; then
        echo "Initializing Alembic..."
        pipenv run alembic init alembic
        
        # Update alembic.ini with DATABASE_URL
        if [ -f "alembic.ini" ]; then
            echo "Updating database URL in alembic.ini..."
            # Use different sed syntax for macOS vs Linux
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s|sqlalchemy.url = .*|sqlalchemy.url = $DATABASE_URL|g" alembic.ini
            else
                # Linux
                sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = $DATABASE_URL|g" alembic.ini
            fi
        else
            echo "WARNING: alembic.ini not found. Please configure it manually."
        fi
        
        echo "Alembic initialized successfully."
    else
        echo "Alembic directory already exists."
        
        # Still update the database URL in alembic.ini if it exists
        if [ -f "alembic.ini" ]; then
            echo "Updating database URL in alembic.ini..."
            # Use different sed syntax for macOS vs Linux
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s|sqlalchemy.url = .*|sqlalchemy.url = $DATABASE_URL|g" alembic.ini
            else
                # Linux
                sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = $DATABASE_URL|g" alembic.ini
            fi
        else
            echo "WARNING: alembic.ini not found. Please configure it manually."
        fi
    fi
}

# Create a new migration
create_migration() {
    local message="$1"
    if [ -z "$message" ]; then
        message="Migration $(date +%Y%m%d%H%M%S)"
    fi
    
    echo "Creating new migration: $message"
    if [ -f "alembic.ini" ]; then
        pipenv run alembic revision --autogenerate -m "$message"
        echo "Migration created successfully."
        echo "Please review the generated migration script before applying it."
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Apply migrations
upgrade_database() {
    echo "Applying migrations..."
    if [ -f "alembic.ini" ]; then
        pipenv run alembic upgrade head
        echo "Migrations applied successfully."
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Downgrade migrations
downgrade_database() {
    local steps="$1"
    if [ -z "$steps" ]; then
        steps=1
    fi
    
    echo "Downgrading $steps migration(s)..."
    if [ -f "alembic.ini" ]; then
        pipenv run alembic downgrade -$steps
        echo "Downgrade completed successfully."
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Reset database
reset_database() {
    echo "Resetting database..."
    if [ -f "alembic.ini" ]; then
        echo "Downgrading to base..."
        pipenv run alembic downgrade base
        
        echo "Upgrading to head..."
        pipenv run alembic upgrade head
        
        echo "Database reset completed successfully."
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Show migration history
show_history() {
    echo "Migration history:"
    if [ -f "alembic.ini" ]; then
        pipenv run alembic history --verbose
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Show current migration version
show_current() {
    echo "Current migration version:"
    if [ -f "alembic.ini" ]; then
        pipenv run alembic current
    else
        echo "ERROR: alembic.ini not found. Please initialize Alembic first."
        exit 1
    fi
}

# Check if alembic.ini exists
check_alembic_config() {
    if [ ! -f "alembic.ini" ]; then
        echo "WARNING: alembic.ini not found."
        read -p "Do you want to initialize Alembic now? (y/n): " answer
        if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
            init_alembic
        else
            echo "Exiting. Please initialize Alembic before running migrations."
            exit 1
        fi
    fi
}

# Main script logic
case "$1" in
    init)
        init_alembic
        ;;
    create)
        check_alembic_config
        create_migration "$2"
        ;;
    upgrade)
        check_alembic_config
        upgrade_database
        ;;
    downgrade)
        check_alembic_config
        downgrade_database "$2"
        ;;
    reset)
        check_alembic_config
        reset_database
        ;;
    history)
        check_alembic_config
        show_history
        ;;
    current)
        check_alembic_config
        show_current
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        if [ -z "$1" ]; then
            # No command provided, show usage
            show_usage
        else
            echo "Unknown command: $1"
            show_usage
            exit 1
        fi
        ;;
esac

exit 0