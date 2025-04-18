import os
from create_issues import close_github_issue

def main():
    # Get token from environment variable
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")
    
    owner = "niklas-joh"
    repo = "plantScraper"
    issue_number = 2  # Issue #2
    
    try:
        # Close issue #2
        response = close_github_issue(token, owner, repo, issue_number)
        print(f"Successfully closed issue #{issue_number}")
        print(f"Issue URL: {response['html_url']}")
    except Exception as e:
        print(f"Error closing issue: {e}")

if __name__ == "__main__":
    main()
