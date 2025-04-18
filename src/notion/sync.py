"""
Synchronization module for Notion integration.

This module provides functions for synchronizing plant data between
the plants_detailed.json file and a Notion database.
"""

import json
import os
import logging
from src.notion import config
from src.notion.client import NotionClient
from src.notion.schema import validate_database_schema, get_database_creation_schema
from src.notion.transformer import transform_plant_to_notion_properties, create_plant_content_blocks

# Set up logging
logger = logging.getLogger(__name__)

def load_plants_data(file_path=None):
    """
    Load plants data from JSON file.
    
    Args:
        file_path (str, optional): Path to JSON file. Defaults to config.PLANTS_DETAILED_JSON.
        
    Returns:
        list: List of plant dictionaries
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = file_path or config.PLANTS_DETAILED_JSON
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Plants data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_plants(client):
    """
    Get existing plants from the Notion database.
    
    Args:
        client (NotionClient): Notion client
        
    Returns:
        dict: Dictionary mapping plant names to page IDs
    """
    plant_page_map = {}
    
    try:
        # Query all pages in the database
        response = client.query_database()
        
        # Extract plant names and page IDs
        for page in response.get("results", []):
            title_property = page["properties"].get("Name", {})
            if "title" in title_property and title_property["title"]:
                plant_name = title_property["title"][0]["text"]["content"]
                plant_page_map[plant_name] = page["id"]
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
    
    return plant_page_map

def ensure_database_exists(client, parent_page_id=None):
    """
    Ensure that the Notion database exists with the correct schema.
    
    Args:
        client (NotionClient): Notion client
        parent_page_id (str, optional): Parent page ID for creating a new database.
            Required if the database doesn't exist. Defaults to None.
            
    Returns:
        bool: True if the database exists or was created, False otherwise
    """
    # Check if database exists
    if client.database_exists():
        # Validate schema
        try:
            database = client.get_database()
            is_valid, missing_properties = validate_database_schema(database)
            
            if is_valid:
                logger.info("Database exists with valid schema")
                return True
            else:
                logger.warning(f"Database exists but has invalid schema. Missing properties: {missing_properties}")
                # We can't modify database schema via API, so we'll have to use it as is
                return True
        except Exception as e:
            logger.error(f"Error validating database schema: {str(e)}")
            return False
    else:
        # Create database if parent page ID is provided
        if not parent_page_id:
            logger.error("Database doesn't exist and no parent page ID provided for creation")
            return False
        
        try:
            # Create database with proper schema
            schema = get_database_creation_schema()
            client.create_database(
                parent_page_id=parent_page_id,
                title="Plant Database",
                properties=schema
            )
            logger.info("Created new database with proper schema")
            return True
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False

def sync_plant_to_notion(client, plant, existing_plants=None):
    """
    Synchronize a single plant to Notion.
    
    Args:
        client (NotionClient): Notion client
        plant (dict): Plant data
        existing_plants (dict, optional): Dictionary mapping plant names to page IDs.
            If not provided, will query the database. Defaults to None.
            
    Returns:
        tuple: (success, action, error_message)
            success (bool): Whether the operation was successful
            action (str): "created", "updated", or "skipped"
            error_message (str): Error message if the operation failed
    """
    if not plant.get("Name"):
        return False, "skipped", "Plant has no name"
    
    try:
        # Get existing plants if not provided
        if existing_plants is None:
            existing_plants = get_existing_plants(client)
        
        # Transform plant data to Notion format
        properties = transform_plant_to_notion_properties(plant)
        content_blocks = create_plant_content_blocks(plant)
        
        # Check if plant already exists
        if plant["Name"] in existing_plants:
            # Update existing page
            page_id = existing_plants[plant["Name"]]
            client.update_page(page_id, properties)
            
            # Update content blocks
            # Note: This requires clearing existing blocks and adding new ones
            # as Notion API doesn't support direct replacement
            
            # Get existing blocks
            blocks = client.get_block_children(page_id)
            
            # Append new blocks
            client.append_block_children(page_id, content_blocks)
            
            return True, "updated", ""
        else:
            # Create new page
            client.create_page(properties, content_blocks)
            return True, "created", ""
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error syncing plant '{plant.get('Name', 'unknown')}': {error_message}")
        return False, "skipped", error_message

def sync_plants_to_notion(plants=None, client=None, parent_page_id=None, file_path=None):
    """
    Synchronize plants data to Notion database.
    
    Args:
        plants (list, optional): List of plant dictionaries. If not provided,
            will load from file_path. Defaults to None.
        client (NotionClient, optional): Notion client. If not provided,
            will create a new client. Defaults to None.
        parent_page_id (str, optional): Parent page ID for creating a new database
            if it doesn't exist. Defaults to None.
        file_path (str, optional): Path to plants JSON file. Defaults to config.PLANTS_DETAILED_JSON.
            
    Returns:
        dict: Synchronization results
    """
    # Initialize client if not provided
    client = client or NotionClient()
    
    # Validate configuration
    is_valid, error_message = config.validate_config()
    if not is_valid:
        return {
            "success": False,
            "error": error_message,
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
    
    # Ensure database exists
    if not ensure_database_exists(client, parent_page_id):
        return {
            "success": False,
            "error": "Database doesn't exist or couldn't be created",
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
    
    # Load plants if not provided
    try:
        plants = plants or load_plants_data(file_path)
    except Exception as e:
        return {
            "success": False,
            "error": f"Error loading plants data: {str(e)}",
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": []
        }
    
    # Get existing plants
    existing_plants = get_existing_plants(client)
    
    # Track results
    results = {
        "success": True,
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process each plant
    for plant in plants:
        success, action, error_message = sync_plant_to_notion(client, plant, existing_plants)
        
        if success:
            if action == "created":
                results["created"] += 1
            elif action == "updated":
                results["updated"] += 1
        else:
            results["skipped"] += 1
            results["errors"].append({
                "plant": plant.get("Name", "unknown"),
                "error": error_message
            })
    
    return results
