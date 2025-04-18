import requests
import os
from typing import Dict, List
import urllib3

# Disable SSL warnings - use this only if you trust the connection
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_github_issue(token: str, owner: str, repo: str, title: str, body: str, labels: List[str]) -> Dict:
    """
    Create a GitHub issue using the REST API.
    
    Args:
        token (str): GitHub personal access token
        owner (str): Repository owner
        repo (str): Repository name
        title (str): Issue title
        body (str): Issue description
        labels (List[str]): List of labels to apply
        
    Returns:
        Dict: Response from GitHub API
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    data = {
        "title": title,
        "body": body,
        "labels": labels
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
    
    owner = "niklas-joh"
    repo = "plantScraper"
    
    # Issue 1: Recipe Links
    recipe_issue = {
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
    }
    
    # Issue 2: Table Formatting
    table_issue = {
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
    }
    
    # Issue 3: Advertisement Text Removal
    ad_removal_issue = {
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
    
    try:
        # Create Recipe Links issue
        recipe_response = create_github_issue(
            token, owner, repo,
            recipe_issue["title"],
            recipe_issue["body"],
            recipe_issue["labels"]
        )
        print(f"Created Recipe Links issue #{recipe_response['number']}")
        
        # Create Table Formatting issue
        table_response = create_github_issue(
            token, owner, repo,
            table_issue["title"],
            table_issue["body"],
            table_issue["labels"]
        )
        print(f"Created Table Formatting issue #{table_response['number']}")
        
        # Create Advertisement Text Removal issue
        ad_removal_response = create_github_issue(
            token, owner, repo,
            ad_removal_issue["title"],
            ad_removal_issue["body"],
            ad_removal_issue["labels"]
        )
        print(f"Created Advertisement Text Removal issue #{ad_removal_response['number']}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating issues: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    main()
