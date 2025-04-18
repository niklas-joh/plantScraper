#!/usr/bin/env python3
"""
Script to clean up additional unused files after project reorganization.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    """Main function to clean up additional unused files."""
    print("\n=== Cleaning Up Additional Unused Files ===\n")
    
    # List of files to remove
    files_to_remove = [
        # Redundant script files
        "scripts/env_comment_issue.py",       # Replaced by scripts/comment_on_issue.py
        "scripts/git_comment_issue.py",       # Replaced by scripts/comment_on_issue.py
        
        # Redundant JSON files
        "project_organization_issue.json",    # Used for issue creation, now redundant
        "sample_issues.json",                 # Sample data, now redundant
        
        # Temporary or redundant data files
        "plants_detailed_with_h3.json",       # Intermediate data file, now redundant
        "plants_detailed.json",               # Moved to output directory
    ]
    
    # Create a backup directory
    backup_dir = "backup_files"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create subdirectories
    scripts_backup_dir = os.path.join(backup_dir, "scripts")
    os.makedirs(scripts_backup_dir, exist_ok=True)
    print(f"Created backup directory: {scripts_backup_dir}")
    
    # Move files to backup directory
    for file in files_to_remove:
        if os.path.exists(file):
            # Determine backup path
            if file.startswith("scripts/"):
                # For script files, preserve the directory structure
                backup_path = os.path.join(backup_dir, file)
            else:
                # For other files, put them directly in the backup directory
                backup_path = os.path.join(backup_dir, os.path.basename(file))
            
            # Create parent directories if needed
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Create backup
            shutil.copy2(file, backup_path)
            print(f"Backed up: {file} -> {backup_path}")
            
            # Remove original file
            os.remove(file)
            print(f"Removed: {file}")
        else:
            print(f"File not found: {file}")
    
    print("\n=== Additional Cleanup Complete ===\n")
    print("The following files have been backed up to the 'backup_files' directory and removed from the main project:")
    for file in files_to_remove:
        backup_path = os.path.join(backup_dir, os.path.basename(file) if not file.startswith("scripts/") else file)
        if os.path.exists(backup_path):
            print(f"- {file}")
    
    print("\nThese files were redundant after the project reorganization, as their functionality has been")
    print("moved to the appropriate modules in the new directory structure or they were temporary files.")

if __name__ == "__main__":
    main()
