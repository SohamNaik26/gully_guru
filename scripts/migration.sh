#!/bin/bash

# Define the path to your Alembic directory and the Alembic executable
ALEMBIC_DIR="./alembic"
ALEMBIC_CMD="alembic"

# Check if Alembic is initialized by looking for the alembic.ini file
if [ ! -f "$ALEMBIC_DIR/alembic.ini" ]; then
    echo "Initializing Alembic..."
    $ALEMBIC_CMD init $ALEMBIC_DIR
    echo "Alembic initialized."
else
    echo "Alembic already initialized."
fi

# Update the database URL in alembic.ini (customize this line according to your setup)
sed -i 's|^sqlalchemy.url.*|sqlalchemy.url = postgresql://user:password@localhost/dbname|' $ALEMBIC_DIR/alembic.ini

# Generate a new migration script if there are model changes
echo "Generating new migration script..."
$ALEMBIC_CMD -c $ALEMBIC_DIR/alembic.ini revision --autogenerate -m "Auto-generated migration"

# Apply migrations to the database
echo "Applying migrations..."
$ALEMBIC_CMD -c $ALEMBIC_DIR/alembic.ini upgrade head

echo "Database migration completed."