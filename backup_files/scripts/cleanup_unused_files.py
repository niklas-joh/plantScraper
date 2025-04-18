#!/usr/bin/env python3
"""
Script to clean up unused files after project reorganization.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    """Main function to clean up unused files."""
    print("\n=== Cleaning Up Unused Files ===\n")
    
    # List of files to remove
    files_to_remove = [
        "plantscraper.py",                    # Replaced by src/scraper/plant_list.py
        "plants_detailed_scraper.py",         # Replaced by src/scraper/plant_details.py
        "plants_detailed_scraper_refactored.py", # Replaced by src/scraper/plant_details.py
        "create_issues.py",                   # Replaced by src/github/create_issues.py
        "update_issue.py",                    # Replaced by src/github/update_issue_secure.py
        "close_issue.py",                     # Replaced by src/github/issue_manager.py
        "test_issue_creation.py",             # Replaced by tests/
        "run_scraper.bat"                     # Replaced by scripts/run_scraper.py
    ]
    
    # Create a backup directory
    backup_dir = "backup_files"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Created backup directory: {backup_dir}")
    
    # Move files to backup directory
    for file in files_to_remove:
        if os.path.exists(file):
            # Create backup
            backup_path = os.path.join(backup_dir, file)
            shutil.copy2(file, backup_path)
            print(f"Backed up: {file} -> {backup_path}")
            
            # Remove original file
            os.remove(file)
            print(f"Removed: {file}")
        else:
            print(f"File not found: {file}")
    
    print("\n=== Cleanup Complete ===\n")
    print("The following files have been backed up to the 'backup_files' directory and removed from the main project:")
    for file in files_to_remove:
        if os.path.exists(os.path.join(backup_dir, file)):
            print(f"- {file}")
    
    print("\nThese files were redundant after the project reorganization, as their functionality has been")
    print("moved to the appropriate modules in the new directory structure.")

if __name__ == "__main__":
    main()
