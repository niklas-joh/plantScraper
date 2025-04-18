#!/usr/bin/env python
"""
Script to create a Notion database with the proper schema.

This script creates a new Notion database with the schema defined in
src/notion/schema.py.
"""

import os
import sys
import argparse
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.notion.schema import get_database_creation_schema

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_notion_database(api_key, parent_page_id, title="Plant Database"):
    """
    Create a Notion database.
    
    Args:
        api_key (str): Notion API key
        parent_page_id (str): Parent page ID
        title (str, optional): Database title. Defaults to "Plant Database".
        
    Returns:
        tuple: (success, database_id, error_message)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Get database schema
    properties = get_database_creation_schema()
    
    # Create database
    payload = {
        "parent": {
            "page_id": parent_page_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": title
                }
            }
        ],
        "properties": properties
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/databases",
            headers=headers,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        database_id = response.json()["id"]
        return True, database_id, ""
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = f"{error_message}: {error_data}"
            except:
                error_message = f"{error_message}: {e.response.text}"
        return False, None, error_message

def main():
    """Create a Notion database."""
    
    # Load environment variables from .env file
    dotenv_path = Path(config.BASE_DIR) / '.env'
    load_dotenv(dotenv_path)
    
    parser = argparse.ArgumentParser(description="Create a Notion database")
    parser.add_argument("--api-key", help="Notion API key")
    parser.add_argument("--parent-page-id", help="Parent page ID")
    parser.add_argument("--title", help="Database title", default="Plant Database")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get API key and parent page ID
    api_key = args.api_key or os.getenv("NOTION_API_KEY")
    parent_page_id = args.parent_page_id or os.getenv("NOTION_PARENT_PAGE_ID")
    
    # Validate API key and parent page ID
    if not api_key:
        logger.error("Notion API key not provided")
        return 1
    
    if not parent_page_id:
        logger.error("Parent page ID not provided")
        return 1
    
    # Create database
    logger.info(f"Creating Notion database '{args.title}'...")
    
    success, database_id, error_message = create_notion_database(
        api_key=api_key,
        parent_page_id=parent_page_id,
        title=args.title
    )
    
    if success:
        logger.info(f"Database created successfully!")
        logger.info(f"Database ID: {database_id}")
        logger.info(f"Add this to your .env file as NOTION_DATABASE_ID={database_id}")
    else:
        logger.error(f"Failed to create database: {error_message}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
