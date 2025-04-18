"""
Secure GitHub issue update functionality.
"""

from src.github.issue_manager import IssueManager

def update_github_issue(token, owner, repo, issue_number, title=None, body=None, state=None, labels=None):
    """
    Update a GitHub issue using the IssueManager.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to update
        title (str, optional): New issue title. Defaults to None.
        body (str, optional): New issue description. Defaults to None.
        state (str, optional): New issue state ('open' or 'closed'). Defaults to None.
        labels (list, optional): New list of labels. Defaults to None.
        
    Returns:
        dict: Response from GitHub API
    """
    issue_manager = IssueManager(token=token, owner=owner, repo=repo)
    return issue_manager.update_issue(issue_number, title, body, state, labels)

def add_comment_to_issue(token, owner, repo, issue_number, body):
    """
    Add a comment to a GitHub issue using the IssueManager.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to comment on
        body (str): Comment text
        
    Returns:
        dict: Response from GitHub API
    """
    issue_manager = IssueManager(token=token, owner=owner, repo=repo)
    return issue_manager.add_comment(issue_number, body)

def close_github_issue(token, owner, repo, issue_number):
    """
    Close a GitHub issue using the IssueManager.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to close
        
    Returns:
        dict: Response from GitHub API
    """
    issue_manager = IssueManager(token=token, owner=owner, repo=repo)
    return issue_manager.close_issue(issue_number)

def get_github_issue(token, owner, repo, issue_number):
    """
    Get a GitHub issue using the IssueManager.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        issue_number (int): Issue number to get
        
    Returns:
        dict: Response from GitHub API
    """
    issue_manager = IssueManager(token=token, owner=owner, repo=repo)
    return issue_manager.get_issue(issue_number)

def list_github_issues(token, owner, repo, state="open", labels=None, sort="created", direction="desc"):
    """
    List GitHub issues using the IssueManager.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        state (str, optional): Issue state ('open', 'closed', 'all'). Defaults to 'open'.
        labels (str, optional): Comma-separated list of label names. Defaults to None.
        sort (str, optional): What to sort results by ('created', 'updated', 'comments'). Defaults to 'created'.
        direction (str, optional): Sort direction ('asc' or 'desc'). Defaults to 'desc'.
        
    Returns:
        list: List of issues
    """
    issue_manager = IssueManager(token=token, owner=owner, repo=repo)
    return issue_manager.list_issues(state, labels, sort, direction)
