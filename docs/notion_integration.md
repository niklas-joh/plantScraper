# Notion Integration for Plant Data

This document outlines the technical details for integrating the plants_detailed.json data with a Notion database.

## Prerequisites

- Notion account with admin access to create integrations
- Python 3.6+
- Access to the GitHub repository for this project

## Notion API Overview

The Notion API allows developers to connect Notion with other tools and services. It provides endpoints for:

- Reading, creating, and updating pages
- Reading, creating, and updating databases
- Managing users, comments, and blocks

For our integration, we'll primarily use the database and page endpoints.

## Setup Process

### 1. Create a Notion Integration

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Name it "Plant Scraper Integration"
4. Select the workspace where you want to use the integration
5. Set the capabilities (Read content, Update content, Insert content)
6. Click "Submit" to create the integration
7. Copy the "Internal Integration Token" for later use

### 2. Create a Notion Database

1. Create a new page in your Notion workspace
2. Add a database (full page)
3. Configure the database with the following properties:
   - Name (Title)
   - Botanical Name (Text)
   - Plant Type (Select)
   - Sun Exposure (Multi-select)
   - Soil pH (Select)
   - Bloom Time (Multi-select)
   - Flower Color (Multi-select)
   - Hardiness Zone (Multi-select)
   - Link (URL)
   - Image URL (URL)
   - Photo Credit (Text)
   - Planting (Text)
   - Growing (Text)
   - Harvesting (Text)
   - Wit and Wisdom (Text)
   - Cooking Notes (Text)
4. Share the database with your integration by clicking "Share" and selecting your integration

Alternatively, you can create a database with just the basic properties and then use the `update_notion_database.py` script to add the additional properties (see below).

### 3. Install Required Dependencies

Add the following to requirements.txt:

```
notion-client==1.0.0
```

## Implementation Details

### Configuration Module

Create a new configuration module for Notion settings:

```python
# src/notion/config.py

import os
from src import config

# Notion API settings
NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# Validation
if not NOTION_API_KEY:
    print("Warning: NOTION_API_KEY environment variable not set")
if not NOTION_DATABASE_ID:
    print("Warning: NOTION_DATABASE_ID environment variable not set")
```

### Notion Client Module

Create a client module to handle Notion API interactions:

```python
# src/notion/client.py

from notion_client import Client
from src.notion import config

class NotionClient:
    """Client for interacting with the Notion API."""
    
    def __init__(self, api_key=None, database_id=None):
        """
        Initialize the Notion client.
        
        Args:
            api_key (str, optional): Notion API key. Defaults to config.NOTION_API_KEY.
            database_id (str, optional): Notion database ID. Defaults to config.NOTION_DATABASE_ID.
        """
        self.api_key = api_key or config.NOTION_API_KEY
        self.database_id = database_id or config.NOTION_DATABASE_ID
        self.client = Client(auth=self.api_key)
    
    def get_database(self):
        """
        Get the Notion database.
        
        Returns:
            dict: Database information
        """
        return self.client.databases.retrieve(self.database_id)
    
    def query_database(self, filter=None, sorts=None):
        """
        Query the Notion database.
        
        Args:
            filter (dict, optional): Filter to apply. Defaults to None.
            sorts (list, optional): Sort order. Defaults to None.
            
        Returns:
            list: List of pages
        """
        return self.client.databases.query(
            database_id=self.database_id,
            filter=filter,
            sorts=sorts
        )
    
    def create_page(self, properties, children=None):
        """
        Create a new page in the database.
        
        Args:
            properties (dict): Page properties
            children (list, optional): Page content blocks. Defaults to None.
            
        Returns:
            dict: Created page
        """
        return self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            children=children or []
        )
    
    def update_page(self, page_id, properties=None, archived=None):
        """
        Update a page in the database.
        
        Args:
            page_id (str): Page ID
            properties (dict, optional): Page properties to update. Defaults to None.
            archived (bool, optional): Whether to archive the page. Defaults to None.
            
        Returns:
            dict: Updated page
        """
        params = {}
        if properties is not None:
            params["properties"] = properties
        if archived is not None:
            params["archived"] = archived
            
        return self.client.pages.update(page_id, **params)
```

### Data Transformation Module

Create a module to transform plant data to Notion format:

```python
# src/notion/transformer.py

def transform_plant_to_notion(plant):
    """
    Transform a plant dictionary to Notion properties format.
    
    Args:
        plant (dict): Plant data from plants_detailed.json
        
    Returns:
        dict: Notion properties
    """
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": plant["Name"]
                    }
                }
            ]
        },
        "Botanical Name": {
            "rich_text": [
                {
                    "text": {
                        "content": plant.get("Botanical Name", "")
                    }
                }
            ]
        },
        "Plant Type": {
            "select": {
                "name": plant.get("Plant Type", "")
            }
        },
        "Link": {
            "url": plant.get("Link", "")
        },
        "Image URL": {
            "url": plant.get("Image URL", "")
        },
        "Photo Credit": {
            "rich_text": [
                {
                    "text": {
                        "content": plant.get("Photo Credit", "")
                    }
                }
            ]
        }
    }
    
    # Handle multi-select properties
    for field in ["Sun Exposure", "Bloom Time", "Flower Color", "Hardiness Zone"]:
        if field in plant and plant[field]:
            values = plant[field].split("\n")
            properties[field] = {
                "multi_select": [{"name": value.strip()} for value in values if value.strip()]
            }
    
    # Handle Soil pH
    if "Soil pH" in plant:
        properties["Soil pH"] = {
            "select": {
                "name": plant["Soil pH"].split("\n")[0].strip()
            }
        }
    
    return properties

def create_pests_diseases_blocks(plant):
    """
    Create Notion blocks for pests/diseases table.
    
    Args:
        plant (dict): Plant data from plants_detailed.json
        
    Returns:
        list: Notion blocks
    """
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Pests and Diseases"}}]
            }
        }
    ]
    
    if "Pests/Diseases" in plant and "headers" in plant["Pests/Diseases"] and "rows" in plant["Pests/Diseases"]:
        # Add table block
        table_block = {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": len(plant["Pests/Diseases"]["headers"]),
                "has_column_header": True,
                "has_row_header": False,
                "children": []
            }
        }
        
        # Add header row
        header_row = {
            "object": "block",
            "type": "table_row",
            "table_row": {
                "cells": [[{"type": "text", "text": {"content": header}}] for header in plant["Pests/Diseases"]["headers"]]
            }
        }
        table_block["table"]["children"].append(header_row)
        
        # Add data rows
        for row in plant["Pests/Diseases"]["rows"]:
            data_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [
                        [{"type": "text", "text": {"content": row.get("pest", "")}}],
                        [{"type": "text", "text": {"content": row.get("type", "")}}],
                        [{"type": "text", "text": {"content": row.get("symptoms", "")}}],
                        [{"type": "text", "text": {"content": row.get("control", "")}}]
                    ]
                }
            }
            table_block["table"]["children"].append(data_row)
        
        blocks.append(table_block)
    
    return blocks

def create_recipes_blocks(plant):
    """
    Create Notion blocks for recipes.
    
    Args:
        plant (dict): Plant data from plants_detailed.json
        
    Returns:
        list: Notion blocks
    """
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Recipes"}}]
            }
        }
    ]
    
    if "Recipes" in plant and isinstance(plant["Recipes"], dict):
        # Add bulleted list for recipes
        for recipe_name, recipe_url in plant["Recipes"].items():
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": recipe_name,
                                "link": {"url": recipe_url}
                            }
                        }
                    ]
                }
            })
    
    return blocks

def create_content_blocks(plant):
    """
    Create Notion blocks for plant content.
    
    Args:
        plant (dict): Plant data from plants_detailed.json
        
    Returns:
        list: Notion blocks
    """
    blocks = []
    
    # Add plant image
    if "Image URL" in plant and plant["Image URL"]:
        blocks.append({
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": plant["Image URL"]
                }
            }
        })
    
    # Add sections for planting, growing, harvesting
    for section in ["Planting", "Growing", "Harvesting"]:
        if section in plant:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": section}}]
                }
            })
            
            # Add content paragraph
            if "content" in plant[section] and plant[section]["content"]:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": plant[section]["content"]}}]
                    }
                })
            
            # Add sub-headings
            if "sub_headings" in plant[section]:
                for sub_heading, content in plant[section]["sub_headings"].items():
                    blocks.append({
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [{"type": "text", "text": {"content": sub_heading}}]
                        }
                    })
                    blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": content}}]
                        }
                    })
    
    # Add pests/diseases table
    blocks.extend(create_pests_diseases_blocks(plant))
    
    # Add recipes
    blocks.extend(create_recipes_blocks(plant))
    
    # Add wit and wisdom
    if "Wit and Wisdom" in plant and plant["Wit and Wisdom"]:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Wit and Wisdom"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": plant["Wit and Wisdom"]}}]
            }
        })
    
    # Add cooking notes
    if "Cooking Notes" in plant and plant["Cooking Notes"]:
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "Cooking Notes"}}]
            }
        })
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": plant["Cooking Notes"]}}]
            }
        })
    
    return blocks
```

### Synchronization Module

Create a module to handle the synchronization between JSON and Notion:

```python
# src/notion/sync.py

import json
import os
from src import config
from src.notion.client import NotionClient
from src.notion.transformer import transform_plant_to_notion, create_content_blocks

def load_plants_data(file_path=None):
    """
    Load plants data from JSON file.
    
    Args:
        file_path (str, optional): Path to JSON file. Defaults to config.PLANTS_DETAILED_JSON.
        
    Returns:
        list: List of plant dictionaries
    """
    file_path = file_path or config.PLANTS_DETAILED_JSON
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Plants data file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def sync_plants_to_notion(plants=None, client=None):
    """
    Synchronize plants data to Notion database.
    
    Args:
        plants (list, optional): List of plant dictionaries. Defaults to None.
        client (NotionClient, optional): Notion client. Defaults to None.
        
    Returns:
        dict: Synchronization results
    """
    # Initialize client if not provided
    client = client or NotionClient()
    
    # Load plants if not provided
    plants = plants or load_plants_data()
    
    # Query existing pages
    existing_pages = client.query_database()
    
    # Create a map of plant names to page IDs
    plant_page_map = {}
    for page in existing_pages.get("results", []):
        title_property = page["properties"].get("Name", {})
        if "title" in title_property and title_property["title"]:
            plant_name = title_property["title"][0]["text"]["content"]
            plant_page_map[plant_name] = page["id"]
    
    # Track results
    results = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "errors": []
    }
    
    # Process each plant
    for plant in plants:
        try:
            # Transform plant data to Notion format
            properties = transform_plant_to_notion(plant)
            
            # Create content blocks
            children = create_content_blocks(plant)
            
            # Check if plant already exists
            if plant["Name"] in plant_page_map:
                # Update existing page
                page_id = plant_page_map[plant["Name"]]
                client.update_page(page_id, properties)
                
                # Note: Updating page content requires a different approach
                # as Notion API doesn't support updating children directly
                # We would need to retrieve existing blocks and update them
                
                results["updated"] += 1
            else:
                # Create new page
                client.create_page(properties, children)
                results["created"] += 1
                
        except Exception as e:
            results["errors"].append({
                "plant": plant["Name"],
                "error": str(e)
            })
            results["skipped"] += 1
    
    return results
```

### Command-Line Script

Create a script to run the synchronization:

```python
# scripts/sync_to_notion.py

#!/usr/bin/env python
"""
Script to synchronize plants data to Notion database.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.notion.sync import sync_plants_to_notion
from src.notion.client import NotionClient

def main():
    """Synchronize plants data to Notion database."""
    
    parser = argparse.ArgumentParser(description="Synchronize plants data to Notion database")
    parser.add_argument("--api-key", help="Notion API key")
    parser.add_argument("--database-id", help="Notion database ID")
    parser.add_argument("--plants-file", help="Path to plants JSON file")
    
    args = parser.parse_args()
    
    # Initialize client with command-line arguments
    client = NotionClient(
        api_key=args.api_key,
        database_id=args.database_id
    )
    
    # Run synchronization
    print("Synchronizing plants data to Notion...")
    results = sync_plants_to_notion(client=client)
    
    # Print results
    print(f"Synchronization complete!")
    print(f"Created: {results['created']}")
    print(f"Updated: {results['updated']}")
    print(f"Skipped: {results['skipped']}")
    
    if results["errors"]:
        print(f"\nErrors occurred during synchronization:")
        for error in results["errors"]:
            print(f"- {error['plant']}: {error['error']}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Testing

Create tests for the Notion integration:

```python
# tests/test_notion_transformer.py

import pytest
from src.notion.transformer import transform_plant_to_notion, create_content_blocks

def test_transform_plant_to_notion():
    """Test transforming plant data to Notion properties."""
    plant = {
        "Name": "Test Plant",
        "Botanical Name": "Testus plantus",
        "Plant Type": "Vegetable",
        "Sun Exposure": "Full Sun\nPart Sun",
        "Soil pH": "Slightly Acidic to Neutral",
        "Link": "https://example.com/plant",
        "Image URL": "https://example.com/image.jpg"
    }
    
    properties = transform_plant_to_notion(plant)
    
    assert properties["Name"]["title"][0]["text"]["content"] == "Test Plant"
    assert properties["Botanical Name"]["rich_text"][0]["text"]["content"] == "Testus plantus"
    assert properties["Plant Type"]["select"]["name"] == "Vegetable"
    assert properties["Link"]["url"] == "https://example.com/plant"
    assert properties["Image URL"]["url"] == "https://example.com/image.jpg"
    assert properties["Sun Exposure"]["multi_select"][0]["name"] == "Full Sun"
    assert properties["Sun Exposure"]["multi_select"][1]["name"] == "Part Sun"
    assert properties["Soil pH"]["select"]["name"] == "Slightly Acidic to Neutral"

def test_create_content_blocks():
    """Test creating content blocks for a plant."""
    plant = {
        "Name": "Test Plant",
        "Image URL": "https://example.com/image.jpg",
        "Planting": {
            "content": "Planting instructions",
            "sub_headings": {
                "When to Plant": "Plant in spring"
            }
        },
        "Pests/Diseases": {
            "headers": ["Pest/Disease", "Type", "Symptoms", "Control/Prevention"],
            "rows": [
                {
                    "pest": "Aphids",
                    "type": "Insect",
                    "symptoms": "Yellow leaves",
                    "control": "Spray with water"
                }
            ]
        },
        "Recipes": {
            "Test Recipe": "https://example.com/recipe"
        },
        "Wit and Wisdom": "Interesting facts",
        "Cooking Notes": "Cooking instructions"
    }
    
    blocks = create_content_blocks(plant)
    
    # Check that we have the expected number of blocks
    assert len(blocks) > 0
    
    # Check image block
    assert blocks[0]["type"] == "image"
    assert blocks[0]["image"]["external"]["url"] == "https://example.com/image.jpg"
    
    # Check for planting section
    planting_heading_index = next((i for i, block in enumerate(blocks) if block["type"] == "heading_2" and block["heading_2"]["rich_text"][0]["text"]["content"] == "Planting"), None)
    assert planting_heading_index is not None
    
    # Check for recipes section
    recipes_heading_index = next((i for i, block in enumerate(blocks) if block["type"] == "heading_2" and block["heading_2"]["rich_text"][0]["text"]["content"] == "Recipes"), None)
    assert recipes_heading_index is not None
```

## Utility Scripts

### update_notion_database.py

This script updates an existing Notion database schema to include all the fields from plants_detailed.json:

```python
# scripts/update_notion_database.py

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
```

To use this script:

1. Make sure you have the required environment variables set:
   - `NOTION_API_KEY`: Your Notion API key
   - `NOTION_DATABASE_ID`: Your Notion database ID

2. Run the script:
   ```
   python scripts/update_notion_database.py
   ```

3. The script will:
   - Get the current schema of your Notion database
   - Compare it with the desired schema defined in src/notion/schema.py
   - Add any missing properties to your database

This is useful when you've already created a Notion database but need to update its schema to include all the fields from plants_detailed.json.

## Deployment Considerations

### Environment Variables

Set the following environment variables:

- `NOTION_API_KEY`: Your Notion API key
- `NOTION_DATABASE_ID`: Your Notion database ID

### Scheduled Synchronization

Consider setting up a scheduled job to synchronize the data periodically:

- Use a cron job on Linux/macOS
- Use Task Scheduler on Windows
- Use GitHub Actions for cloud-based scheduling

### Error Handling

The synchronization process includes error handling to:

- Skip plants that fail to synchronize
- Report detailed error information
- Continue processing despite individual failures

### Rate Limiting

Notion API has rate limits:

- 3 requests per second (per token)
- 90 requests per minute (per token)

The synchronization process should include throttling to avoid hitting these limits.

## Future Enhancements

- Two-way synchronization (Notion to JSON)
- Web interface for managing the integration
- Support for images stored in Notion
- Improved content formatting
- Support for comments and discussions
