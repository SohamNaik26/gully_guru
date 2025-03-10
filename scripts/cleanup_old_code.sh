#!/bin/bash
# Cleanup script to remove old code directories that are no longer needed
# with the new feature-based structure

echo "Starting cleanup of old code directories..."

# Define the project root
PROJECT_ROOT="/Users/jaynaik/Desktop/GullyGuru"

# Remove old handlers directory
echo "Removing old handlers directory..."
rm -rf "$PROJECT_ROOT/src/bot/handlers"

# Remove old callbacks directory
echo "Removing old callbacks directory..."
rm -rf "$PROJECT_ROOT/src/bot/callbacks"

# Remove old keyboards directory
echo "Removing old keyboards directory..."
rm -rf "$PROJECT_ROOT/src/bot/keyboards"

echo "Cleanup complete!" 