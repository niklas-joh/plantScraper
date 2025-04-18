#!/usr/bin/env python
"""
Script to update an existing Notion database schema.

This script updates an existing Notion database with the schema defined in
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

def get_database_schema(api_key, database_id):
    """
    Get the current schema of a Notion database.
    
    Args:
        api_key (str): Notion API key
        database_id (str): Database ID
        
    Returns:
        tuple: (success, properties, error_message)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28"
    }
    
    try:
        response = requests.get(
            f"https://api.notion.com/v1/databases/{database_id}",
            headers=headers,
            verify=False
        )
        
        response.raise_for_status()
        properties = response.json().get("properties", {})
        return True, properties, ""
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = f"{error_message}: {error_data}"
            except:
                error_message = f"{error_message}: {e.response.text}"
        return False, None, error_message

def update_database_schema(api_key, database_id, properties_to_add):
    """
    Update the schema of a Notion database.
    
    Args:
        api_key (str): Notion API key
        database_id (str): Database ID
        properties_to_add (dict): Properties to add to the database
        
    Returns:
        tuple: (success, error_message)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Create payload
    payload = {
        "properties": properties_to_add
    }
    
    try:
        response = requests.patch(
            f"https://api.notion.com/v1/databases/{database_id}",
            headers=headers,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        return True, ""
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = f"{error_message}: {error_data}"
            except:
                error_message = f"{error_message}: {e.response.text}"
        return False, error_message

def main():
    """Update a Notion database schema."""
    
    # Load environment variables from .env file
    dotenv_path = Path(config.BASE_DIR) / '.env'
    load_dotenv(dotenv_path)
    
    parser = argparse.ArgumentParser(description="Update a Notion database schema")
    parser.add_argument("--api-key", help="Notion API key")
    parser.add_argument("--database-id", help="Database ID")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get API key and database ID
    api_key = args.api_key or os.getenv("NOTION_API_KEY")
    database_id = args.database_id or os.getenv("NOTION_DATABASE_ID")
    
    # Validate API key and database ID
    if not api_key:
        logger.error("Notion API key not provided")
        return 1
    
    if not database_id:
        logger.error("Database ID not provided")
        return 1
    
    # Get current database schema
    logger.info(f"Getting current schema for database {database_id}...")
    
    success, current_properties, error_message = get_database_schema(
        api_key=api_key,
        database_id=database_id
    )
    
    if not success:
        logger.error(f"Failed to get database schema: {error_message}")
        return 1
    
    # Get desired schema
    desired_properties = get_database_creation_schema()
    
    # Determine properties to add
    properties_to_add = {}
    for prop_name, prop_config in desired_properties.items():
        if prop_name not in current_properties:
            logger.info(f"Adding property: {prop_name}")
            properties_to_add[prop_name] = prop_config
    
    if not properties_to_add:
        logger.info("No properties to add. Database schema is up to date.")
        return 0
    
    # Update database schema
    logger.info(f"Updating database schema with {len(properties_to_add)} new properties...")
    
    success, error_message = update_database_schema(
        api_key=api_key,
        database_id=database_id,
        properties_to_add=properties_to_add
    )
    
    if success:
        logger.info(f"Database schema updated successfully!")
        for prop_name in properties_to_add:
            logger.info(f"Added property: {prop_name}")
    else:
        logger.error(f"Failed to update database schema: {error_message}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
