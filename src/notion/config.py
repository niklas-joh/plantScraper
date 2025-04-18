"""
Configuration module for Notion integration.

This module provides configuration settings for the Notion API integration,
including API key and database ID handling.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use scripts/sync_to_notion_requests.py instead, which directly handles
configuration through environment variables.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The src.notion.config module is deprecated and will be removed in a future version. "
    "Please use scripts/sync_to_notion_requests.py instead.",
    DeprecationWarning,
    stacklevel=2
)

import os
from pathlib import Path
from dotenv import load_dotenv
from src import config

# Load environment variables from .env file
dotenv_path = Path(config.BASE_DIR) / '.env'
load_dotenv(dotenv_path)

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
