"""
Configuration module for Notion integration.

This module provides configuration settings for the Notion API integration,
including API key and database ID handling.
"""

import os
from src import config

# Notion API settings
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# Path to plants detailed JSON file
PLANTS_DETAILED_JSON = config.PLANTS_DETAILED_JSON

# Notion API rate limits
NOTION_RATE_LIMIT_PER_SECOND = 3
NOTION_RATE_LIMIT_PER_MINUTE = 90

# Validation
def validate_config():
    """
    Validate the Notion configuration.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not NOTION_API_KEY:
        return False, "NOTION_API_KEY environment variable not set"
    
    if not NOTION_DATABASE_ID:
        return False, "NOTION_DATABASE_ID environment variable not set"
    
    return True, ""
