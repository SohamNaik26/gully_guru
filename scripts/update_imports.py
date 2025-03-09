#!/usr/bin/env python3
"""
Script to update imports of api_client_instance in the bot code.
This script replaces 'from src.bot.api_client_instance import api_client'
with 'from src.api.api_client_instance import api_client' in all Python files
in the src/bot directory.
"""

import os
import re
from pathlib import Path


def update_imports(directory):
    """Update imports in all Python files in the given directory."""
    pattern = re.compile(r"from src\.bot\.api_client_instance import api_client")
    replacement = "from src.api.api_client_instance import api_client"

    # Get all Python files in the directory and its subdirectories
    python_files = list(Path(directory).glob("**/*.py"))

    for file_path in python_files:
        # Read the file content
        with open(file_path, "r") as file:
            content = file.read()

        # Replace the import statement
        updated_content = pattern.sub(replacement, content)

        # Write the updated content back to the file
        if content != updated_content:
            print(f"Updating imports in {file_path}")
            with open(file_path, "w") as file:
                file.write(updated_content)


if __name__ == "__main__":
    # Update imports in the src/bot directory
    bot_directory = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "bot"
    )
    update_imports(bot_directory)
    print("Import updates completed.")
