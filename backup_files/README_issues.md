# Dynamic GitHub Issue Creation

This tool allows you to dynamically create GitHub issues from JSON files or using the default template issues.

## Prerequisites

- Python 3.6+
- GitHub Personal Access Token with appropriate permissions
- Required Python packages: `requests`

## Environment Variables

Set the following environment variables:

- `GITHUB_TOKEN` (required): Your GitHub Personal Access Token
- `GITHUB_OWNER` (optional): The repository owner (defaults to "niklas-joh")
- `GITHUB_REPO` (optional): The repository name (defaults to "plantScraper")

## Usage

### Using Default Issues

To create the default set of issues:

```bash
python create_issues.py
```

### Using Custom Issues from JSON File

To create issues from a custom JSON file:

```bash
python create_issues.py sample_issues.json
```

## JSON File Format

The JSON file should contain an array of issue objects, each with the following structure:

```json
[
  {
    "title": "Issue Title",
    "body": "Issue description and details",
    "labels": ["label1", "label2"]
  },
  {
    "title": "Another Issue",
    "body": "More details...",
    "labels": ["bug", "high-priority"]
  }
]
```

### Required Fields

- `title`: The title of the issue
- `body`: The description and details of the issue

### Optional Fields

- `labels`: An array of label strings to apply to the issue (defaults to empty array if not provided)

## Example

A sample JSON file (`sample_issues.json`) is included in this repository. You can use it as a template for creating your own issue files:

```bash
python create_issues.py sample_issues.json
```

## Programmatic Usage

You can also use the functions in this script programmatically:

```python
from create_issues import create_issues_from_list, load_issues_from_json

# Load issues from a JSON file
issues = load_issues_from_json("path/to/issues.json")

# Or create a custom list of issues
custom_issues = [
    {
        "title": "Custom Issue",
        "body": "Issue details...",
        "labels": ["custom-label"]
    }
]

# Create the issues
token = "your_github_token"
owner = "repository_owner"
repo = "repository_name"
create_issues_from_list(token, owner, repo, custom_issues)
```

## Error Handling

The script includes error handling for:
- Missing GitHub token
- Invalid JSON format
- File not found
- API request failures

Error messages will be displayed in the console with details to help troubleshoot the issue.
