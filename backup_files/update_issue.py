import requests
import os
import json
import sys
import urllib3

# Disable SSL warnings - use this only if you trust the connection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def update_github_issue(token: str, owner: str, repo: str, issue_number: int, body: str = None, title: str = None, labels: list = None):
    """
    Update a GitHub issue using the REST API.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to update
        body (str, optional): New issue description
        title (str, optional): New issue title
        labels (list, optional): New list of labels
        
    Returns:
        dict: Response from GitHub API
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # Only include parameters that are provided
    data = {}
    if body is not None:
        data["body"] = body
    if title is not None:
        data["title"] = title
    if labels is not None:
        data["labels"] = labels
    
    try:
        # Disable SSL verification - use this only if you trust the connection
        response = requests.patch(url, headers=headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise

def add_comment_to_issue(token: str, owner: str, repo: str, issue_number: int, comment: str):
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
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "body": comment
    }
    
    try:
        # Disable SSL verification - use this only if you trust the connection
        response = requests.post(url, headers=headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise

def main():
    # Get token from environment variable
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")
    
    # Default repository information
    owner = os.getenv("GITHUB_OWNER", "niklas-joh")
    repo = os.getenv("GITHUB_REPO", "plantScraper")
    
    # Check for command line arguments
    if len(sys.argv) < 3:
        print("Usage: python update_issue.py <issue_number> <comment|update> [file_path]")
        print("  - issue_number: The issue number to update")
        print("  - comment|update: Whether to add a comment or update the issue body")
        print("  - file_path: Optional path to a file containing the comment or new body")
        sys.exit(1)
    
    issue_number = int(sys.argv[1])
    action = sys.argv[2]
    
    # Get content from file or stdin
    content = ""
    if len(sys.argv) > 3:
        file_path = sys.argv[3]
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            sys.exit(1)
    else:
        print("Enter content (Ctrl+D or Ctrl+Z to end):")
        try:
            content = sys.stdin.read()
        except Exception as e:
            print(f"Error reading input: {str(e)}")
            sys.exit(1)
    
    try:
        if action.lower() == "comment":
            response = add_comment_to_issue(token, owner, repo, issue_number, content)
            print(f"Successfully added comment to issue #{issue_number}")
            print(f"Comment URL: {response['html_url']}")
        elif action.lower() == "update":
            response = update_github_issue(token, owner, repo, issue_number, body=content)
            print(f"Successfully updated issue #{issue_number}")
            print(f"Issue URL: {response['html_url']}")
        else:
            print(f"Unknown action: {action}")
            print("Use 'comment' to add a comment or 'update' to update the issue body")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
