"""
GitHub issue creation functionality.
"""

import os
import json
import sys
from src.github.issue_manager import IssueManager
from src import config

def load_issues_from_json(json_file_path):
    """
    Load issues from a JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file containing issues
        
    Returns:
        list: List of issue dictionaries
    """
    try:
        with open(json_file_path, 'r') as f:
            issues = json.load(f)
        
        # Validate the structure
        if not isinstance(issues, list):
            raise ValueError("JSON file must contain a list of issues")
        
        for i, issue in enumerate(issues):
            if not isinstance(issue, dict):
                raise ValueError(f"Issue at index {i} is not a dictionary")
            if "title" not in issue:
                raise ValueError(f"Issue at index {i} is missing 'title'")
            if "body" not in issue:
                raise ValueError(f"Issue at index {i} is missing 'body'")
        
        return issues
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")

def get_default_issues():
    """
    Get a list of default issues for demonstration purposes.
    
    Returns:
        list: List of default issue dictionaries
    """
    return [
        {
            "title": "Enhancement: Add Recipe Links to Recipe Section",
            "body": """Currently, the recipe section only includes recipe names without their corresponding links. This enhancement will:

1. Functionality Changes:
   - Capture recipe URLs during scraping
   - Store recipe links alongside recipe names in JSON output
   - Maintain existing recipe name formatting

2. Technical Implementation:
   - Update process_field_with_subheadings() to extract recipe links
   - Modify JSON structure to store recipe links
   - Update documentation to reflect new data structure

3. Expected Output Format:
```json
"Recipes": {
    "Pasta Salad With Spinach and Artichokes": "https://www.almanac.com/recipe/...",
    "Shrimp and Artichoke Casserole": "https://www.almanac.com/recipe/..."
}
```

4. Acceptance Criteria:
   - All recipe links are correctly captured
   - JSON structure maintains backward compatibility
   - Links are valid and accessible
   - Documentation is updated""",
            "labels": ["enhancement"]
        },
        {
            "title": "Enhancement: Preserve Table Formatting for Pest/Diseases Section",
            "body": """Currently, the pest/diseases section loses its table formatting when stored in JSON. This enhancement will:

1. Functionality Changes:
   - Preserve table structure from HTML
   - Maintain column headers and relationships
   - Keep formatting consistent across all plant entries

2. Technical Implementation:
   - Update process_table() function to maintain structure
   - Modify JSON schema to accommodate table format
   - Add table validation to ensure consistency

3. Expected Output Format:
```json
"Pests/Diseases": {
    "headers": ["Pest/Disease", "Type", "Symptoms", "Control/Prevention"],
    "rows": [
        {
            "pest": "Aphids",
            "type": "Insect",
            "symptoms": "Misshapen/yellow leaves...",
            "control": "Knock off with water spray..."
        }
    ]
}
```

4. Acceptance Criteria:
   - Table structure is preserved
   - Headers are correctly captured
   - Row relationships are maintained
   - Data is easily parseable
   - Documentation is updated""",
            "labels": ["enhancement"]
        },
        {
            "title": "Bug: Advertisement Text Showing in Cooking Notes Section",
            "body": """Currently, advertisement text is showing up in the Cooking Notes section despite our code to remove it. This bug fix will:

1. Problem Description:
   - Advertisement text with markers like "ADVERTISEMENT" and "Advertisement" appears in the Cooking Notes section
   - The clean_advertisement_content() function exists but is not being properly applied to all content

2. Technical Implementation:
   - Enhance the clean_advertisement_content() function to handle multiple occurrences of advertisement text
   - Apply the function consistently to all content, especially in the Cooking Notes section
   - Handle different variations of advertisement text (e.g., "ADVERTISEMENT", "Advertisement")

3. Expected Outcome:
   - All advertisement text is removed from the final JSON output
   - Content before advertisements is preserved
   - Multiple occurrences of advertisements in the same content are all removed

4. Acceptance Criteria:
   - No "ADVERTISEMENT" text appears in any section of the JSON output
   - Content quality and readability is maintained
   - The solution is robust against different advertisement text variations""",
            "labels": ["bug"]
        }
    ]

def create_issues(token=None, owner=None, repo=None, json_file_path=None):
    """
    Create GitHub issues from a JSON file or default issues.
    
    Args:
        token (str, optional): GitHub token. If not provided, will be retrieved from TokenManager.
        owner (str, optional): Repository owner. Defaults to config.GITHUB_OWNER.
        repo (str, optional): Repository name. Defaults to config.GITHUB_REPO.
        json_file_path (str, optional): Path to JSON file with issues. Defaults to None.
        
    Returns:
        list: List of responses from GitHub API
    """
    try:
        # Create issue manager
        issue_manager = IssueManager(token=token, owner=owner, repo=repo)
        
        # Load issues from JSON file if provided
        if json_file_path:
            print(f"Loading issues from {json_file_path}")
            issues = load_issues_from_json(json_file_path)
        else:
            # Use default issues if no file provided
            print("No JSON file provided. Using default issues.")
            issues = get_default_issues()
        
        # Create the issues
        return issue_manager.create_issues_from_list(issues)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main function to run the issue creator."""
    # Check for command line arguments
    json_file_path = None
    
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    
    # Create the issues
    create_issues(json_file_path=json_file_path)

if __name__ == "__main__":
    main()
