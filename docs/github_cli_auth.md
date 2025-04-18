# GitHub CLI Authentication Options

This document outlines different methods for authenticating with GitHub when creating issues programmatically.

## Option 1: Using GitHub CLI with 1Password Integration

If you have GitHub CLI (`gh`) installed and integrated with 1Password, you can use it to create issues directly without needing to manage tokens manually.

### Prerequisites
- GitHub CLI (`gh`) installed
- 1Password CLI installed and configured
- 1Password integration with GitHub CLI set up

### Setup Steps

1. **Install GitHub CLI** (if not already installed)
   ```bash
   # For Windows with Chocolatey
   choco install gh
   
   # For macOS with Homebrew
   brew install gh
   
   # For Linux
   # See https://github.com/cli/cli/blob/trunk/docs/install_linux.md
   ```

2. **Install 1Password CLI** (if not already installed)
   ```bash
   # For Windows with Chocolatey
   choco install 1password-cli
   
   # For macOS with Homebrew
   brew install --cask 1password/tap/1password-cli
   
   # For Linux
   # See https://developer.1password.com/docs/cli/get-started/
   ```

3. **Authenticate GitHub CLI with 1Password**
   ```bash
   # Login to GitHub CLI
   gh auth login
   
   # Follow the prompts to authenticate with GitHub
   # Select "Login with a web browser" when prompted
   ```

4. **Configure 1Password Integration with GitHub CLI**
   ```bash
   # Enable 1Password integration with GitHub CLI
   gh auth setup-git --hostname github.com
   
   # Follow the prompts to set up 1Password integration
   ```

### Creating Issues with GitHub CLI

Once authenticated, you can create issues directly using the GitHub CLI:

```bash
gh issue create --repo niklas-joh/plantScraper --title "Enhancement: Integrate plants_detailed.json with Notion Database" --body-file notion_integration_issue_body.md --label enhancement --label integration --label notion
```

To use this with our existing JSON file, you'll need to extract the body content:

```python
# scripts/create_issue_with_gh_cli.py
import json
import os
import subprocess
from pathlib import Path

def main():
    # Path to the issue JSON file
    issue_file = os.path.join(Path(__file__).resolve().parent.parent, "notion_integration_issue.json")
    
    # Check if the file exists
    if not os.path.exists(issue_file):
        print(f"Error: Issue file not found at {issue_file}")
        return 1
    
    # Load the issue data
    with open(issue_file, 'r') as f:
        issues = json.load(f)
    
    if not issues:
        print("Error: No issues found in the JSON file")
        return 1
    
    # Get the first issue
    issue = issues[0]
    
    # Extract the title, body, and labels
    title = issue.get("title", "")
    body = issue.get("body", "")
    labels = issue.get("labels", [])
    
    # Write the body to a temporary file
    body_file = os.path.join(Path(__file__).resolve().parent.parent, "temp_issue_body.md")
    with open(body_file, 'w') as f:
        f.write(body)
    
    # Construct the GitHub CLI command
    cmd = ["gh", "issue", "create", 
           "--repo", "niklas-joh/plantScraper",
           "--title", title,
           "--body-file", body_file]
    
    # Add labels
    for label in labels:
        cmd.extend(["--label", label])
    
    # Execute the command
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"Successfully created issue: {result.stdout}")
        
        # Clean up the temporary file
        os.remove(body_file)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating issue: {e.stderr}")
        return 1
    finally:
        # Make sure to clean up the temporary file even if an error occurs
        if os.path.exists(body_file):
            os.remove(body_file)

if __name__ == "__main__":
    exit(main())
```

## Option 2: Using GitHub CLI with Environment Variables

If you prefer not to use 1Password integration, you can authenticate GitHub CLI using environment variables.

### Setup Steps

1. **Generate a GitHub Personal Access Token**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with the `repo` scope
   - Copy the token

2. **Set the Environment Variable**
   ```bash
   # For Windows
   set GH_TOKEN=your_token_here
   
   # For macOS/Linux
   export GH_TOKEN=your_token_here
   ```

3. **Verify Authentication**
   ```bash
   gh auth status
   ```

## Option 3: Using the GitHub API Directly

This is the approach used in our current implementation with the `IssueManager` class. It requires setting the `GITHUB_TOKEN` environment variable.

### Setup Steps

1. **Generate a GitHub Personal Access Token**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with the `repo` scope
   - Copy the token

2. **Set the Environment Variable**
   ```bash
   # For Windows
   set GITHUB_TOKEN=your_token_here
   
   # For macOS/Linux
   export GITHUB_TOKEN=your_token_here
   ```

3. **Run the Issue Creation Script**
   ```bash
   python scripts/create_notion_integration_issue.py
   ```

## Recommendation

If you already have 1Password with GitHub CLI installed, Option 1 is the most secure and convenient approach. It leverages your existing authentication setup and doesn't require managing tokens manually.

To implement this approach:

1. Create the `scripts/create_issue_with_gh_cli.py` script as shown above
2. Run the script to create the issue using GitHub CLI with 1Password integration
