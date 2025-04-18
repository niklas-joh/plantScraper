"""
Transformer module for converting plant data to Notion format.

This module provides functions for transforming plant data from the
plants_detailed.json format to Notion's API format for properties and content.

DEPRECATED: This module is deprecated and will be removed in a future version.
Please use scripts/sync_to_notion_requests.py instead, which includes its own
transformation functions.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The src.notion.transformer module is deprecated and will be removed in a future version. "
    "Please use scripts/sync_to_notion_requests.py instead.",
    DeprecationWarning,
    stacklevel=2
)

def transform_plant_to_notion_properties(plant):
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
                        "content": plant.get("Name", "")
                    }
                }
            ]
        }
    }
    
    # Add text properties
    for field in ["Botanical Name", "Photo Credit"]:
        if field in plant and plant[field]:
            properties[field] = {
                "rich_text": [
                    {
                        "text": {
                            "content": plant[field]
                        }
                    }
                ]
            }
    
    # Add URL properties
    for field in ["Link", "Image URL"]:
        if field in plant and plant[field]:
            properties[field] = {
                "url": plant[field]
            }
    
    # Add select properties
    for field in ["Plant Type", "Soil pH"]:
        if field in plant and plant[field]:
            # Take the first value if it's a multi-line string
            value = plant[field].split("\n")[0].strip() if "\n" in plant[field] else plant[field].strip()
            if value:
                properties[field] = {
                    "select": {
                        "name": value
                    }
                }
    
    # Add multi-select properties
    for field in ["Sun Exposure", "Bloom Time", "Flower Color", "Hardiness Zone"]:
        if field in plant and plant[field]:
            values = plant[field].split("\n") if "\n" in plant[field] else [plant[field]]
            if values:
                properties[field] = {
                    "multi_select": [
                        {"name": value.strip()} for value in values if value.strip()
                    ]
                }
    
    # Add rich text properties for content sections
    for field in ["Planting", "Growing", "Harvesting", "Wit and Wisdom", "Cooking Notes"]:
        if field in plant:
            content = ""
            if isinstance(plant[field], dict) and "content" in plant[field]:
                content = plant[field]["content"]
                
                # Add sub-headings if they exist
                if "sub_headings" in plant[field]:
                    for sub_heading, sub_content in plant[field]["sub_headings"].items():
                        content += f"\n\n{sub_heading}:\n{sub_content}"
            elif isinstance(plant[field], str):
                content = plant[field]
                
            if content:
                # Truncate content if it's too long for a property (Notion has a limit)
                max_length = 2000
                if len(content) > max_length:
                    content = content[:max_length-3] + "..."
                    
                properties[field] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
    
    return properties

def create_rich_text_block(content):
    """
    Create a rich text paragraph block.
    
    Args:
        content (str): Text content
        
    Returns:
        dict: Notion paragraph block
    """
    if not content:
        return None
    
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content
                    }
                }
            ]
        }
    }

def create_heading_block(content, level=2):
    """
    Create a heading block.
    
    Args:
        content (str): Heading text
        level (int, optional): Heading level (1-3). Defaults to 2.
        
    Returns:
        dict: Notion heading block
    """
    if not content:
        return None
    
    heading_type = f"heading_{level}"
    return {
        "object": "block",
        "type": heading_type,
        heading_type: {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": content
                    }
                }
            ]
        }
    }

def create_image_block(url):
    """
    Create an image block.
    
    Args:
        url (str): Image URL
        
    Returns:
        dict: Notion image block
    """
    if not url:
        return None
    
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {
                "url": url
            }
        }
    }

def create_bulleted_list_item(content, link=None):
    """
    Create a bulleted list item.
    
    Args:
        content (str): Item text
        link (str, optional): URL to link to. Defaults to None.
        
    Returns:
        dict: Notion bulleted list item block
    """
    if not content:
        return None
    
    text_obj = {
        "type": "text",
        "text": {
            "content": content
        }
    }
    
    if link:
        text_obj["text"]["link"] = {"url": link}
    
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [text_obj]
        }
    }

def create_table_block(headers, rows):
    """
    Create a table block.
    
    Args:
        headers (list): Table headers
        rows (list): Table rows
        
    Returns:
        dict: Notion table block
    """
    if not headers or not rows:
        return None
    
    table_width = len(headers)
    table_children = []
    
    # Add header row
    header_row = {
        "object": "block",
        "type": "table_row",
        "table_row": {
            "cells": [[{"type": "text", "text": {"content": header}}] for header in headers]
        }
    }
    table_children.append(header_row)
    
    # Add data rows
    for row in rows:
        if isinstance(row, dict):
            # Handle dictionary rows (like pests/diseases)
            cells = []
            for header in headers:
                header_key = header.lower().replace("/", "_").replace(" ", "_")
                cells.append([{"type": "text", "text": {"content": row.get(header_key, "")}}])
            
            data_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": cells
                }
            }
        else:
            # Handle list rows
            data_row = {
                "object": "block",
                "type": "table_row",
                "table_row": {
                    "cells": [[{"type": "text", "text": {"content": str(cell)}}] for cell in row]
                }
            }
        
        table_children.append(data_row)
    
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": table_width,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_children
        }
    }

def create_plant_content_blocks(plant):
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
        image_block = create_image_block(plant["Image URL"])
        if image_block:
            blocks.append(image_block)
    
    # Add sections for planting, growing, harvesting
    for section in ["Planting", "Growing", "Harvesting"]:
        if section in plant:
            # Add section heading
            heading_block = create_heading_block(section)
            if heading_block:
                blocks.append(heading_block)
            
            # Add content paragraph
            if "content" in plant[section] and plant[section]["content"]:
                content_block = create_rich_text_block(plant[section]["content"])
                if content_block:
                    blocks.append(content_block)
            
            # Add sub-headings
            if "sub_headings" in plant[section]:
                for sub_heading, content in plant[section]["sub_headings"].items():
                    sub_heading_block = create_heading_block(sub_heading, level=3)
                    if sub_heading_block:
                        blocks.append(sub_heading_block)
                    
                    content_block = create_rich_text_block(content)
                    if content_block:
                        blocks.append(content_block)
    
    # Add pests/diseases table
    if "Pests/Diseases" in plant and "headers" in plant["Pests/Diseases"] and "rows" in plant["Pests/Diseases"]:
        # Add section heading
        heading_block = create_heading_block("Pests and Diseases")
        if heading_block:
            blocks.append(heading_block)
        
        # Create table
        headers = plant["Pests/Diseases"]["headers"]
        rows = plant["Pests/Diseases"]["rows"]
        
        table_block = create_table_block(headers, rows)
        if table_block:
            blocks.append(table_block)
    
    # Add recipes
    if "Recipes" in plant and isinstance(plant["Recipes"], dict) and plant["Recipes"]:
        # Add section heading
        heading_block = create_heading_block("Recipes")
        if heading_block:
            blocks.append(heading_block)
        
        # Add bulleted list for recipes
        for recipe_name, recipe_url in plant["Recipes"].items():
            list_item = create_bulleted_list_item(recipe_name, link=recipe_url)
            if list_item:
                blocks.append(list_item)
    
    # Add wit and wisdom
    if "Wit and Wisdom" in plant and plant["Wit and Wisdom"]:
        heading_block = create_heading_block("Wit and Wisdom")
        if heading_block:
            blocks.append(heading_block)
        
        content_block = create_rich_text_block(plant["Wit and Wisdom"])
        if content_block:
            blocks.append(content_block)
    
    # Add cooking notes
    if "Cooking Notes" in plant and plant["Cooking Notes"]:
        heading_block = create_heading_block("Cooking Notes")
        if heading_block:
            blocks.append(heading_block)
        
        content_block = create_rich_text_block(plant["Cooking Notes"])
        if content_block:
            blocks.append(content_block)
    
    return blocks
