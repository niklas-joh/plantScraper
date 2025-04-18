#!/usr/bin/env python
"""
Script to create a GitHub issue for Notion integration using GitHub CLI.
This script is designed to work with GitHub CLI and 1Password integration.
"""

import json
import os
import subprocess
from pathlib import Path

def main():
    """Create the Notion integration GitHub issue using GitHub CLI."""
    
    # Path to the issue JSON file
    issue_file = os.path.join(Path(__file__).resolve().parent.parent, "notion_integration_issue.json")
    
    # Check if the file exists
    if not os.path.exists(issue_file):
        print(f"Error: Issue file not found at {issue_file}")
        return 1
    
    # Load the issue data
    try:
        with open(issue_file, 'r', encoding='utf-8') as f:
            issues = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in issue file: {str(e)}")
        return 1
    except Exception as e:
        print(f"Error reading issue file: {str(e)}")
        return 1
    
    if not issues:
        print("Error: No issues found in the JSON file")
        return 1
    
    # Get the first issue
    issue = issues[0]
    
    # Extract the title, body, and labels
    title = issue.get("title", "")
    body = issue.get("body", "")
    labels = issue.get("labels", [])
    
    if not title or not body:
        print("Error: Issue must have a title and body")
        return 1
    
    # Write the body to a temporary file
    body_file = os.path.join(Path(__file__).resolve().parent.parent, "temp_issue_body.md")
    try:
        with open(body_file, 'w', encoding='utf-8') as f:
            f.write(body)
    except Exception as e:
        print(f"Error writing temporary body file: {str(e)}")
        return 1
    
    # Check if GitHub CLI is installed
    try:
        subprocess.run(["gh", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("Error: GitHub CLI (gh) is not installed or not in PATH")
        print("Please install GitHub CLI: https://cli.github.com/")
        if os.path.exists(body_file):
            os.remove(body_file)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"Error checking GitHub CLI: {e.stderr}")
        if os.path.exists(body_file):
            os.remove(body_file)
        return 1
    
    # Check if authenticated with GitHub
    try:
        auth_result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if auth_result.returncode != 0:
            print("Error: Not authenticated with GitHub")
            print("Please run 'gh auth login' to authenticate")
            print("\nSee docs/github_cli_auth.md for more information")
            if os.path.exists(body_file):
                os.remove(body_file)
            return 1
    except subprocess.CalledProcessError as e:
        print(f"Error checking GitHub authentication: {e.stderr}")
        if os.path.exists(body_file):
            os.remove(body_file)
        return 1
    
    # Check if labels exist and create them if they don't
    print("Checking and creating labels if needed...")
    for label in labels:
        # Check if label exists
        check_cmd = ["gh", "label", "list", "--repo", "niklas-joh/plantScraper", "--json", "name"]
        try:
            result = subprocess.run(check_cmd, check=True, capture_output=True, text=True)
            label_list = json.loads(result.stdout)
            label_names = [label_obj["name"] for label_obj in label_list]
            
            if label not in label_names:
                print(f"Creating label: {label}")
                create_label_cmd = ["gh", "label", "create", label, "--repo", "niklas-joh/plantScraper"]
                subprocess.run(create_label_cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not check or create label '{label}': {e.stderr}")
            print("Continuing without this label...")
            labels.remove(label)
        except json.JSONDecodeError:
            print(f"Warning: Could not parse label list. Continuing without label '{label}'...")
            labels.remove(label)
    
    # Construct the GitHub CLI command
    cmd = ["gh", "issue", "create", 
           "--repo", "niklas-joh/plantScraper",
           "--title", title,
           "--body-file", body_file]
    
    # Add labels (only those that exist or were successfully created)
    for label in labels:
        cmd.extend(["--label", label])
    
    # Execute the command
    try:
        print("Creating GitHub issue...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully created issue: {result.stdout.strip()}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue: {e.stderr}")
        return 1
    finally:
        # Clean up the temporary file
        if os.path.exists(body_file):
            os.remove(body_file)

if __name__ == "__main__":
    exit(main())
