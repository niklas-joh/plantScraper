#!/usr/bin/env python
"""
Script to synchronize plants data to Notion database.

This script synchronizes plant data from the plants_detailed.json file
to a Notion database, allowing for better visualization and collaboration.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.notion.client import NotionClient
from src.notion.sync import sync_plants_to_notion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Synchronize plants data to Notion database."""
    
    parser = argparse.ArgumentParser(description="Synchronize plants data to Notion database")
    parser.add_argument("--api-key", help="Notion API key")
    parser.add_argument("--database-id", help="Notion database ID")
    parser.add_argument("--plants-file", help="Path to plants JSON file", 
                        default=config.PLANTS_DETAILED_JSON)
    parser.add_argument("--parent-page-id", help="Parent page ID for creating a new database")
    parser.add_argument("--limit", type=int, help="Limit the number of plants to sync")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set environment variables if provided
    if args.api_key:
        os.environ["NOTION_API_KEY"] = args.api_key
    
    if args.database_id:
        os.environ["NOTION_DATABASE_ID"] = args.database_id
    
    # Check if plants file exists
    if not os.path.exists(args.plants_file):
        logger.error(f"Plants file not found at {args.plants_file}")
        return 1
    
    # Initialize Notion client
    client = NotionClient()
    
    # Sync plants to Notion
    logger.info(f"Synchronizing plants from {args.plants_file} to Notion...")
    
    results = sync_plants_to_notion(
        client=client,
        parent_page_id=args.parent_page_id,
        file_path=args.plants_file
    )
    
    # Print results
    if results["success"]:
        logger.info("Synchronization completed successfully!")
        logger.info(f"Created: {results['created']}")
        logger.info(f"Updated: {results['updated']}")
        logger.info(f"Skipped: {results['skipped']}")
        
        if results["errors"]:
            logger.warning(f"{len(results['errors'])} errors occurred during synchronization:")
            for error in results["errors"]:
                logger.warning(f"- {error['plant']}: {error['error']}")
    else:
        logger.error(f"Synchronization failed: {results.get('error', 'Unknown error')}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
