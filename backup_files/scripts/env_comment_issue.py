#!/usr/bin/env python3
"""
Script to add a comment to a GitHub issue using an environment variable for the token.
"""

import os
import sys
import requests
import argparse
import urllib3
import getpass
from pathlib import Path

# Disable SSL warnings - use this only if you trust the connection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def add_comment_to_issue(token, owner, repo, issue_number, comment):
    """
    Add a comment to a GitHub issue using the REST API.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to comment on
        comment (str): Comment text
        
    Returns:
        dict: Response from GitHub API
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"token {token}",  # Changed from "Bearer" to "token"
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "body": comment
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        # Disable SSL verification - use this only if you trust the connection
        response = requests.post(url, headers=headers, json=data, verify=False)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Add a comment to a GitHub issue")
    parser.add_argument("issue_number", type=int, help="Issue number to comment on")
    parser.add_argument("--owner", default="niklas-joh", help="Repository owner (default: niklas-joh)")
    parser.add_argument("--repo", default="plantScraper", help="Repository name (default: plantScraper)")
    parser.add_argument("--file", "-f", help="Path to a file containing the comment")
    parser.add_argument("--token", help="GitHub token (if not provided, will use GITHUB_TOKEN environment variable)")
    
    args = parser.parse_args()
    
    # Get the token from environment variable or command line
    token = args.token or os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print("GitHub token not found in environment variable GITHUB_TOKEN or command line argument.")
        print("Please enter your GitHub token:")
        token = getpass.getpass()
    
    # Get comment content from file or stdin
    content = ""
    if args.file:
        try:
            with open(args.file, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            sys.exit(1)
    else:
        print("Enter your comment (Ctrl+D or Ctrl+Z to end):")
        try:
            content = sys.stdin.read()
        except Exception as e:
            print(f"Error reading input: {str(e)}")
            sys.exit(1)
    
    if not content.strip():
        print("Comment content cannot be empty.")
        sys.exit(1)
    
    # Add the comment
    try:
        print(f"Adding comment to issue #{args.issue_number}...")
        response = add_comment_to_issue(token, args.owner, args.repo, args.issue_number, content)
        print(f"\n✅ Comment added successfully!")
        print(f"Comment URL: {response['html_url']}")
    except Exception as e:
        print(f"\n❌ Error adding comment: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
