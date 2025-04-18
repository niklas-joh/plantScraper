import json
import os
from create_issues import load_issues_from_json, get_default_issues

def test_issue_loading():
    """
    Test loading issues from a JSON file and from default issues.
    This is a dry run that doesn't make any API calls.
    """
    print("=== Testing Issue Creation Script ===")
    
    # Test loading from sample JSON file
    try:
        print("\n1. Testing loading issues from sample_issues.json:")
        issues = load_issues_from_json("sample_issues.json")
        print(f"Successfully loaded {len(issues)} issues from sample_issues.json")
        
        for i, issue in enumerate(issues, 1):
            print(f"\nIssue {i}:")
            print(f"  Title: {issue['title']}")
            print(f"  Labels: {', '.join(issue.get('labels', []))}")
            print(f"  Body length: {len(issue['body'])} characters")
    except Exception as e:
        print(f"Error loading from sample_issues.json: {str(e)}")
    
    # Test loading default issues
    try:
        print("\n2. Testing loading default issues:")
        issues = get_default_issues()
        print(f"Successfully loaded {len(issues)} default issues")
        
        for i, issue in enumerate(issues, 1):
            print(f"\nDefault Issue {i}:")
            print(f"  Title: {issue['title']}")
            print(f"  Labels: {', '.join(issue.get('labels', []))}")
            print(f"  Body length: {len(issue['body'])} characters")
    except Exception as e:
        print(f"Error loading default issues: {str(e)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_issue_loading()
