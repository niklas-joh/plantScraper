"""
GitHub issue management functionality.
"""

import requests
import json
import urllib3
from src.github.token_manager import TokenManager
from src import config

# Disable SSL warnings if configured
if not config.VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IssueManager:
    """GitHub issue management functionality."""
    
    def __init__(self, token=None, owner=None, repo=None):
        """
        Initialize the issue manager.
        
        Args:
            token (str, optional): GitHub token. If not provided, will be retrieved from TokenManager.
            owner (str, optional): Repository owner. Defaults to config.GITHUB_OWNER.
            repo (str, optional): Repository name. Defaults to config.GITHUB_REPO.
        """
        self.token = token or TokenManager().get_token()
        if not self.token:
            raise ValueError("GitHub token not found. Set GITHUB_TOKEN environment variable or use TokenManager to store a token.")
        
        self.owner = owner or config.GITHUB_OWNER
        self.repo = repo or config.GITHUB_REPO
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def create_issue(self, title, body, labels=None):
        """
        Create a GitHub issue.
        
        Args:
            title (str): Issue title
            body (str): Issue description
            labels (list, optional): List of labels to apply. Defaults to None.
            
        Returns:
            dict: Response from GitHub API
        """
        url = f"{self.base_url}/issues"
        
        data = {
            "title": title,
            "body": body
        }
        
        if labels:
            data["labels"] = labels
        
        try:
            response = requests.post(url, headers=self.headers, json=data, verify=config.VERIFY_SSL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise
    
    def update_issue(self, issue_number, title=None, body=None, state=None, labels=None):
        """
        Update a GitHub issue.
        
        Args:
            issue_number (int): Issue number to update
            title (str, optional): New issue title. Defaults to None.
            body (str, optional): New issue description. Defaults to None.
            state (str, optional): New issue state ('open' or 'closed'). Defaults to None.
            labels (list, optional): New list of labels. Defaults to None.
            
        Returns:
            dict: Response from GitHub API
        """
        url = f"{self.base_url}/issues/{issue_number}"
        
        data = {}
        if title is not None:
            data["title"] = title
        if body is not None:
            data["body"] = body
        if state is not None:
            data["state"] = state
        if labels is not None:
            data["labels"] = labels
        
        try:
            response = requests.patch(url, headers=self.headers, json=data, verify=config.VERIFY_SSL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise
    
    def close_issue(self, issue_number):
        """
        Close a GitHub issue.
        
        Args:
            issue_number (int): Issue number to close
            
        Returns:
            dict: Response from GitHub API
        """
        return self.update_issue(issue_number, state="closed")
    
    def add_comment(self, issue_number, body):
        """
        Add a comment to a GitHub issue.
        
        Args:
            issue_number (int): Issue number to comment on
            body (str): Comment text
            
        Returns:
            dict: Response from GitHub API
        """
        url = f"{self.base_url}/issues/{issue_number}/comments"
        
        data = {
            "body": body
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, verify=config.VERIFY_SSL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise
    
    def get_issue(self, issue_number):
        """
        Get a GitHub issue.
        
        Args:
            issue_number (int): Issue number to get
            
        Returns:
            dict: Response from GitHub API
        """
        url = f"{self.base_url}/issues/{issue_number}"
        
        try:
            response = requests.get(url, headers=self.headers, verify=config.VERIFY_SSL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise
    
    def list_issues(self, state="open", labels=None, sort="created", direction="desc"):
        """
        List GitHub issues.
        
        Args:
            state (str, optional): Issue state ('open', 'closed', 'all'). Defaults to 'open'.
            labels (str, optional): Comma-separated list of label names. Defaults to None.
            sort (str, optional): What to sort results by ('created', 'updated', 'comments'). Defaults to 'created'.
            direction (str, optional): Sort direction ('asc' or 'desc'). Defaults to 'desc'.
            
        Returns:
            list: List of issues
        """
        url = f"{self.base_url}/issues"
        
        params = {
            "state": state,
            "sort": sort,
            "direction": direction
        }
        
        if labels:
            params["labels"] = labels
        
        try:
            response = requests.get(url, headers=self.headers, params=params, verify=config.VERIFY_SSL)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self._handle_request_error(e)
            raise
    
    def create_issues_from_list(self, issues):
        """
        Create multiple GitHub issues from a list of issue dictionaries.
        
        Args:
            issues (list): List of issue dictionaries with keys: title, body, labels
            
        Returns:
            list: List of responses from GitHub API
        """
        responses = []
        
        for issue in issues:
            try:
                response = self.create_issue(
                    issue["title"],
                    issue["body"],
                    issue.get("labels", [])  # Use empty list if labels not provided
                )
                responses.append(response)
                print(f"Created issue #{response['number']}: {issue['title']}")
            except Exception as e:
                print(f"Error creating issue '{issue['title']}': {str(e)}")
        
        return responses
    
    def _handle_request_error(self, exception):
        """
        Handle request exceptions by printing detailed error information.
        
        Args:
            exception: RequestException object
        """
        print(f"Error making request: {str(exception)}")
        if hasattr(exception, 'response') and exception.response is not None:
            print(f"Response status code: {exception.response.status_code}")
            print(f"Response body: {exception.response.text}")
