"""
Notion client module for interacting with the Notion API.

This module provides a client class for interacting with the Notion API,
including methods for retrieving, creating, and updating pages and databases.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use scripts/sync_to_notion_requests.py instead, which directly uses
the requests library to interact with the Notion API.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The src.notion.client module is deprecated and will be removed in a future version. "
    "Please use scripts/sync_to_notion_requests.py instead.",
    DeprecationWarning,
    stacklevel=2
)

import time
import logging
import ssl
import certifi
import httpx
from notion_client import Client
from notion_client.errors import APIResponseError
from src.notion import config

# Create a custom SSL context that doesn't verify certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Set up logging
logger = logging.getLogger(__name__)

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
        self.last_request_time = 0
    
    def _throttle_requests(self):
        """
        Throttle requests to respect Notion API rate limits.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        # Ensure at least 1/3 second between requests (3 requests per second limit)
        if time_since_last_request < (1 / config.NOTION_RATE_LIMIT_PER_SECOND):
            sleep_time = (1 / config.NOTION_RATE_LIMIT_PER_SECOND) - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_database(self):
        """
        Get the Notion database.
        
        Returns:
            dict: Database information
        
        Raises:
            APIResponseError: If the database doesn't exist or can't be accessed
        """
        self._throttle_requests()
        try:
            return self.client.databases.retrieve(self.database_id)
        except APIResponseError as e:
            logger.error(f"Error retrieving database: {str(e)}")
            raise
    
    def database_exists(self):
        """
        Check if the database exists and is accessible.
        
        Returns:
            bool: True if the database exists and is accessible, False otherwise
        """
        try:
            self.get_database()
            return True
        except APIResponseError:
            return False
    
    def query_database(self, filter=None, sorts=None):
        """
        Query the Notion database.
        
        Args:
            filter (dict, optional): Filter to apply. Defaults to None.
            sorts (list, optional): Sort order. Defaults to None.
            
        Returns:
            dict: Query results
        """
        self._throttle_requests()
        return self.client.databases.query(
            database_id=self.database_id,
            filter=filter,
            sorts=sorts
        )
    
    def create_database(self, parent_page_id, title, properties):
        """
        Create a new Notion database.
        
        Args:
            parent_page_id (str): ID of the parent page
            title (str): Database title
            properties (dict): Database properties schema
            
        Returns:
            dict: Created database
        """
        self._throttle_requests()
        return self.client.databases.create(
            parent={"page_id": parent_page_id},
            title=[{
                "type": "text",
                "text": {
                    "content": title
                }
            }],
            properties=properties
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
        self._throttle_requests()
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
        self._throttle_requests()
        params = {}
        if properties is not None:
            params["properties"] = properties
        if archived is not None:
            params["archived"] = archived
            
        return self.client.pages.update(page_id, **params)
    
    def get_page(self, page_id):
        """
        Get a page by ID.
        
        Args:
            page_id (str): Page ID
            
        Returns:
            dict: Page information
        """
        self._throttle_requests()
        return self.client.pages.retrieve(page_id)
    
    def get_block_children(self, block_id):
        """
        Get the children of a block.
        
        Args:
            block_id (str): Block ID
            
        Returns:
            dict: Block children
        """
        self._throttle_requests()
        return self.client.blocks.children.list(block_id)
    
    def append_block_children(self, block_id, children):
        """
        Append children to a block.
        
        Args:
            block_id (str): Block ID
            children (list): Block children to append
            
        Returns:
            dict: Updated block children
        """
        self._throttle_requests()
        return self.client.blocks.children.append(block_id, children=children)
