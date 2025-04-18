#!/usr/bin/env python
"""
Script to synchronize plants data to Notion database using requests.

This script synchronizes plant data from the plants_detailed.json file
to a Notion database, using the requests library directly.
"""

import os
import sys
import json
import time
import argparse
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_plants_data(file_path):
    """
    Load plants data from JSON file.
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        list: List of plant dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def transform_plant_to_notion_properties(plant):
    """
    Transform a plant dictionary to Notion properties format.
    
    Args:
        plant (dict): Plant data
        
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
        }
    }
    
    # Add Botanical Name if available
    if "Botanical Name" in plant:
        properties["Botanical Name"] = {
            "rich_text": [
                {
                    "text": {
                        "content": plant["Botanical Name"]
                    }
                }
            ]
        }
    
    # Add Plant Type if available
    if "Plant Type" in plant:
        properties["Plant Type"] = {
            "select": {
                "name": plant["Plant Type"]
            }
        }
    
    # Add Sun Exposure if available
    if "Sun Exposure" in plant:
        values = plant["Sun Exposure"].split("\n")
        properties["Sun Exposure"] = {
            "multi_select": [{"name": value.strip()} for value in values if value.strip()]
        }
    
    # Add Soil pH if available
    if "Soil pH" in plant:
        properties["Soil pH"] = {
            "select": {
                "name": plant["Soil pH"].split("\n")[0].strip()
            }
        }
    
    # Add Bloom Time if available
    if "Bloom Time" in plant:
        values = plant["Bloom Time"].split("\n")
        properties["Bloom Time"] = {
            "multi_select": [{"name": value.strip()} for value in values if value.strip()]
        }
    
    # Add Flower Color if available
    if "Flower Color" in plant:
        values = plant["Flower Color"].split("\n")
        properties["Flower Color"] = {
            "multi_select": [{"name": value.strip()} for value in values if value.strip()]
        }
    
    # Add Hardiness Zone if available
    if "Hardiness Zone" in plant:
        values = plant["Hardiness Zone"].split("\n")
        properties["Hardiness Zone"] = {
            "multi_select": [{"name": value.strip()} for value in values if value.strip()]
        }
    
    # Add Link if available
    if "Link" in plant:
        properties["Link"] = {
            "url": plant["Link"]
        }
    
    # Add Image URL if available
    if "Image URL" in plant:
        properties["Image URL"] = {
            "url": plant["Image URL"]
        }
    
    # Add Photo Credit if available
    if "Photo Credit" in plant:
        properties["Photo Credit"] = {
            "rich_text": [
                {
                    "text": {
                        "content": plant["Photo Credit"]
                    }
                }
            ]
        }
    
    return properties

def create_plant_content_blocks(plant):
    """
    Create content blocks for a plant.
    
    Args:
        plant (dict): Plant data
        
    Returns:
        list: Content blocks
    """
    blocks = []
    
    # Add description if available
    if "Description" in plant:
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": plant["Description"]
                        }
                    }
                ]
            }
        })
    
    # Add image if available
    if "Image URL" in plant:
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
    
    return blocks

def sync_plant_to_notion(api_key, database_id, plant):
    """
    Sync a plant to Notion.
    
    Args:
        api_key (str): Notion API key
        database_id (str): Notion database ID
        plant (dict): Plant data
        
    Returns:
        tuple: (success, action, error_message)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Transform plant data to Notion format
    properties = transform_plant_to_notion_properties(plant)
    children = create_plant_content_blocks(plant)
    
    # Create page in Notion
    payload = {
        "parent": {
            "database_id": database_id
        },
        "properties": properties,
        "children": children
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        return True, "created", ""
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                error_message = f"{error_message}: {json.dumps(error_data, indent=2)}"
            except:
                error_message = f"{error_message}: {e.response.text}"
        return False, "skipped", error_message

def main():
    """Synchronize plants data to Notion database."""
    
    # Load environment variables from .env file
    dotenv_path = Path(config.BASE_DIR) / '.env'
    load_dotenv(dotenv_path)
    
    parser = argparse.ArgumentParser(description="Synchronize plants data to Notion database")
    parser.add_argument("--api-key", help="Notion API key")
    parser.add_argument("--database-id", help="Notion database ID")
    parser.add_argument("--plants-file", help="Path to plants JSON file", 
                        default=config.PLANTS_DETAILED_JSON)
    parser.add_argument("--limit", type=int, help="Limit the number of plants to sync")
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
        logger.error("Notion database ID not provided")
        return 1
    
    # Check if plants file exists
    if not os.path.exists(args.plants_file):
        logger.error(f"Plants file not found at {args.plants_file}")
        return 1
    
    # Load plants data
    logger.info(f"Loading plants data from {args.plants_file}")
    plants = load_plants_data(args.plants_file)
    
    # Limit the number of plants if specified
    if args.limit:
        plants = plants[:args.limit]
    
    # Sync plants to Notion
    logger.info(f"Synchronizing {len(plants)} plants to Notion...")
    
    results = {
        "created": 0,
        "skipped": 0,
        "errors": []
    }
    
    for i, plant in enumerate(plants):
        logger.info(f"Syncing plant {i+1}/{len(plants)}: {plant.get('Name', 'unknown')}")
        
        success, action, error_message = sync_plant_to_notion(api_key, database_id, plant)
        
        if success:
            results["created"] += 1
        else:
            results["skipped"] += 1
            results["errors"].append({
                "plant": plant.get("Name", "unknown"),
                "error": error_message
            })
        
        # Sleep to avoid rate limiting
        time.sleep(0.5)
    
    # Print results
    logger.info("Synchronization completed!")
    logger.info(f"Created: {results['created']}")
    logger.info(f"Skipped: {results['skipped']}")
    
    if results["errors"]:
        logger.warning(f"{len(results['errors'])} errors occurred during synchronization:")
        for error in results["errors"]:
            logger.warning(f"- {error['plant']}: {error['error']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
