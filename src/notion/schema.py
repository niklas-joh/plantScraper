"""
Schema module for Notion database.

This module defines the schema for the Notion database and provides
functions for validating and creating the database schema.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use scripts/sync_to_notion_requests.py instead, which directly handles
the Notion database schema.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The src.notion.schema module is deprecated and will be removed in a future version. "
    "Please use scripts/sync_to_notion_requests.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# Define the database schema for plant data
PLANT_DATABASE_SCHEMA = {
    "Name": {
        "title": {}
    },
    "Botanical Name": {
        "rich_text": {}
    },
    "Plant Type": {
        "select": {}
    },
    "Sun Exposure": {
        "multi_select": {}
    },
    "Soil pH": {
        "select": {}
    },
    "Bloom Time": {
        "multi_select": {}
    },
    "Flower Color": {
        "multi_select": {}
    },
    "Hardiness Zone": {
        "multi_select": {}
    },
    "Link": {
        "url": {}
    },
    "Image URL": {
        "url": {}
    },
    "Photo Credit": {
        "rich_text": {}
    },
    "Planting": {
        "rich_text": {}
    },
    "Growing": {
        "rich_text": {}
    },
    "Harvesting": {
        "rich_text": {}
    },
    "Wit and Wisdom": {
        "rich_text": {}
    },
    "Cooking Notes": {
        "rich_text": {}
    }
    # Note: Pests/Diseases and Recipes will be handled as tables in page content
}

def validate_database_schema(database):
    """
    Validate that a database has the required schema.
    
    Args:
        database (dict): Database object from Notion API
        
    Returns:
        tuple: (is_valid, missing_properties)
    """
    if not database or "properties" not in database:
        return False, list(PLANT_DATABASE_SCHEMA.keys())
    
    properties = database["properties"]
    missing_properties = []
    
    for prop_name, prop_config in PLANT_DATABASE_SCHEMA.items():
        # Check if property exists
        if prop_name not in properties:
            missing_properties.append(prop_name)
            continue
        
        # Check if property has the correct type
        prop_type = next(iter(prop_config.keys()))
        if prop_type not in properties[prop_name]:
            missing_properties.append(prop_name)
    
    return len(missing_properties) == 0, missing_properties

def get_database_creation_schema():
    """
    Get the schema for creating a new database.
    
    Returns:
        dict: Database schema for creation
    """
    return PLANT_DATABASE_SCHEMA
