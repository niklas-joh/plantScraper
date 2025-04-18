#!/usr/bin/env python
"""
Script to clean up redundant files in the scripts directory.
"""

import os
import sys
from pathlib import Path

def main():
    """Remove redundant script files."""
    
    # Files to remove
    redundant_files = [
        "comment_on_issue.py",
        "create_notion_integration_issue.py"
    ]
    
    # Get the scripts directory
    scripts_dir = Path(__file__).resolve().parent
    
    print("Cleaning up redundant script files...")
    
    # Remove each redundant file
    for file in redundant_files:
        file_path = os.path.join(scripts_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Removed {file}")
            except Exception as e:
                print(f"✗ Failed to remove {file}: {str(e)}")
        else:
            print(f"! File not found: {file}")
    
    print("\nCleanup complete!")
    print("\nRemaining scripts:")
    for file in sorted(os.listdir(scripts_dir)):
        if file.endswith(".py"):
            print(f"- {file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
