"""
Secure token manager for GitHub API authentication.
"""

import os
import json
from pathlib import Path

class TokenManager:
    """Secure token manager for GitHub API authentication."""
    
    def __init__(self, token_file=None):
        """
        Initialize the token manager.
        
        Args:
            token_file (str, optional): Path to the token file. Defaults to ~/.github_token.
        """
        self.token_file = token_file or os.path.join(str(Path.home()), '.github_token')
    
    def get_token(self):
        """
        Get the GitHub token.
        
        Returns:
            str: GitHub token or None if not found
        """
        # First check environment variable
        token = os.getenv("GITHUB_TOKEN")
        if token:
            return token
        
        # Then check token file
        if not os.path.exists(self.token_file):
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                data = json.load(f)
            
            # If token is stored in plain text
            if 'token' in data:
                return data['token']
            
            return None
        except Exception as e:
            print(f"Error reading token file: {str(e)}")
            return None
    
    def store_token(self, token, username=None):
        """
        Store the GitHub token.
        
        Args:
            token (str): GitHub token to store
            username (str, optional): GitHub username. If not provided, will prompt.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not username:
            username = input("Enter your GitHub username: ")
        
        try:
            # Store the token in plain text (for testing only)
            data = {
                'username': username,
                'token': token
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(data, f)
            
            # Set permissions to user only
            os.chmod(self.token_file, 0o600)
            
            return True
        except Exception as e:
            print(f"Error storing token: {str(e)}")
            return False
