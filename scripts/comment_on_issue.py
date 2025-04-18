#!/usr/bin/env python3
"""
Script to add a comment to a GitHub issue.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.github.token_manager import TokenManager
from src.github.update_issue_secure import add_comment_to_issue

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Add a comment to a GitHub issue")
    parser.add_argument("issue_number", type=int, help="The issue number to comment on")
    parser.add_argument("--file", "-f", help="Path to a file containing the comment")
    parser.add_argument("--owner", help="Repository owner (default: from env or config)")
    parser.add_argument("--repo", help="Repository name (default: from env or config)")
    parser.add_argument("--store-token", action="store_true", 
                        help="Store a new GitHub token before proceeding")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Get repository information
    owner = args.owner or os.getenv("GITHUB_OWNER")
    repo = args.repo or os.getenv("GITHUB_REPO")
    
    # Get token from TokenManager
    token_manager = TokenManager()
    
    # Store a new token if requested
    if args.store_token:
        import getpass
        username = input("Enter your GitHub username: ")
        token = getpass.getpass("Enter your GitHub token: ")
        if token_manager.store_token(token, username):
            print("Token stored successfully")
        else:
            print("Failed to store token")
            sys.exit(1)
    
    # Get the token
    token = token_manager.get_token()
    
    if not token:
        print("GitHub token not found. Run with --store-token to store a token.")
        sys.exit(1)
    
    # Get comment content from file or stdin
    comment = ""
    if args.file:
        try:
            with open(args.file, 'r') as f:
                comment = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            sys.exit(1)
    else:
        print("Enter comment (Ctrl+D or Ctrl+Z to end):")
        try:
            comment = sys.stdin.read()
        except Exception as e:
            print(f"Error reading input: {str(e)}")
            sys.exit(1)
    
    try:
        response = add_comment_to_issue(token, owner, repo, args.issue_number, comment)
        print(f"Successfully added comment to issue #{args.issue_number}")
        print(f"Comment URL: {response['html_url']}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
