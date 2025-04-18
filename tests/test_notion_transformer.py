"""
Tests for the Notion transformer module.

This module contains tests for the transformer functions that convert
plant data to Notion format.
"""

import pytest
from src.notion.transformer import (
    transform_plant_to_notion_properties,
    create_rich_text_block,
    create_heading_block,
    create_image_block,
    create_bulleted_list_item,
    create_table_block,
    create_plant_content_blocks
)

def test_transform_plant_to_notion_properties():
    """Test transforming plant data to Notion properties."""
    # Create a sample plant
    plant = {
        "Name": "Test Plant",
        "Botanical Name": "Testus plantus",
        "Plant Type": "Vegetable",
        "Sun Exposure": "Full Sun\nPart Sun",
        "Soil pH": "Slightly Acidic to Neutral",
        "Link": "https://example.com/plant",
        "Image URL": "https://example.com/image.jpg",
        "Photo Credit": "Test Photographer",
        "Planting": {
            "content": "Planting instructions",
            "sub_headings": {
                "When to Plant": "Plant in spring"
            }
        },
        "Growing": {
            "content": "Growing instructions"
        },
        "Harvesting": {
            "content": "Harvesting instructions"
        },
        "Wit and Wisdom": "Interesting facts",
        "Cooking Notes": "Cooking instructions"
    }
    
    # Transform to Notion properties
    properties = transform_plant_to_notion_properties(plant)
    
    # Verify the transformation
    assert properties["Name"]["title"][0]["text"]["content"] == "Test Plant"
    assert properties["Botanical Name"]["rich_text"][0]["text"]["content"] == "Testus plantus"
    assert properties["Plant Type"]["select"]["name"] == "Vegetable"
    assert properties["Link"]["url"] == "https://example.com/plant"
    assert properties["Image URL"]["url"] == "https://example.com/image.jpg"
    assert properties["Photo Credit"]["rich_text"][0]["text"]["content"] == "Test Photographer"
    assert properties["Sun Exposure"]["multi_select"][0]["name"] == "Full Sun"
    assert properties["Sun Exposure"]["multi_select"][1]["name"] == "Part Sun"
    assert properties["Soil pH"]["select"]["name"] == "Slightly Acidic to Neutral"
    
    # Verify the new rich text properties
    assert "Planting" in properties
    assert properties["Planting"]["rich_text"][0]["text"]["content"].startswith("Planting instructions")
    assert "When to Plant" in properties["Planting"]["rich_text"][0]["text"]["content"]
    
    assert "Growing" in properties
    assert properties["Growing"]["rich_text"][0]["text"]["content"] == "Growing instructions"
    
    assert "Harvesting" in properties
    assert properties["Harvesting"]["rich_text"][0]["text"]["content"] == "Harvesting instructions"
    
    assert "Wit and Wisdom" in properties
    assert properties["Wit and Wisdom"]["rich_text"][0]["text"]["content"] == "Interesting facts"
    
    assert "Cooking Notes" in properties
    assert properties["Cooking Notes"]["rich_text"][0]["text"]["content"] == "Cooking instructions"

def test_create_rich_text_block():
    """Test creating a rich text block."""
    # Create a rich text block
    block = create_rich_text_block("Test content")
    
    # Verify the block
    assert block["type"] == "paragraph"
    assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Test content"
    
    # Test with empty content
    assert create_rich_text_block("") is None
    assert create_rich_text_block(None) is None

def test_create_heading_block():
    """Test creating a heading block."""
    # Create heading blocks with different levels
    h2_block = create_heading_block("Test Heading")
    h1_block = create_heading_block("Test Heading", level=1)
    h3_block = create_heading_block("Test Heading", level=3)
    
    # Verify the blocks
    assert h2_block["type"] == "heading_2"
    assert h2_block["heading_2"]["rich_text"][0]["text"]["content"] == "Test Heading"
    
    assert h1_block["type"] == "heading_1"
    assert h1_block["heading_1"]["rich_text"][0]["text"]["content"] == "Test Heading"
    
    assert h3_block["type"] == "heading_3"
    assert h3_block["heading_3"]["rich_text"][0]["text"]["content"] == "Test Heading"
    
    # Test with empty content
    assert create_heading_block("") is None
    assert create_heading_block(None) is None

def test_create_image_block():
    """Test creating an image block."""
    # Create an image block
    block = create_image_block("https://example.com/image.jpg")
    
    # Verify the block
    assert block["type"] == "image"
    assert block["image"]["external"]["url"] == "https://example.com/image.jpg"
    
    # Test with empty URL
    assert create_image_block("") is None
    assert create_image_block(None) is None

def test_create_bulleted_list_item():
    """Test creating a bulleted list item."""
    # Create a bulleted list item
    block = create_bulleted_list_item("Test item")
    
    # Verify the block
    assert block["type"] == "bulleted_list_item"
    assert block["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "Test item"
    
    # Create a bulleted list item with a link
    block_with_link = create_bulleted_list_item("Test item", link="https://example.com")
    
    # Verify the block with link
    assert block_with_link["type"] == "bulleted_list_item"
    assert block_with_link["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "Test item"
    assert block_with_link["bulleted_list_item"]["rich_text"][0]["text"]["link"]["url"] == "https://example.com"
    
    # Test with empty content
    assert create_bulleted_list_item("") is None
    assert create_bulleted_list_item(None) is None

def test_create_table_block():
    """Test creating a table block."""
    # Create a table block
    headers = ["Header 1", "Header 2", "Header 3"]
    rows = [
        ["Row 1, Cell 1", "Row 1, Cell 2", "Row 1, Cell 3"],
        ["Row 2, Cell 1", "Row 2, Cell 2", "Row 2, Cell 3"]
    ]
    
    block = create_table_block(headers, rows)
    
    # Verify the block
    assert block["type"] == "table"
    assert block["table"]["table_width"] == 3
    assert block["table"]["has_column_header"] is True
    assert len(block["table"]["children"]) == 3  # Header row + 2 data rows
    
    # Verify header row
    header_row = block["table"]["children"][0]
    assert header_row["type"] == "table_row"
    assert header_row["table_row"]["cells"][0][0]["text"]["content"] == "Header 1"
    assert header_row["table_row"]["cells"][1][0]["text"]["content"] == "Header 2"
    assert header_row["table_row"]["cells"][2][0]["text"]["content"] == "Header 3"
    
    # Verify data rows
    data_row_1 = block["table"]["children"][1]
    assert data_row_1["type"] == "table_row"
    assert data_row_1["table_row"]["cells"][0][0]["text"]["content"] == "Row 1, Cell 1"
    assert data_row_1["table_row"]["cells"][1][0]["text"]["content"] == "Row 1, Cell 2"
    assert data_row_1["table_row"]["cells"][2][0]["text"]["content"] == "Row 1, Cell 3"
    
    data_row_2 = block["table"]["children"][2]
    assert data_row_2["type"] == "table_row"
    assert data_row_2["table_row"]["cells"][0][0]["text"]["content"] == "Row 2, Cell 1"
    assert data_row_2["table_row"]["cells"][1][0]["text"]["content"] == "Row 2, Cell 2"
    assert data_row_2["table_row"]["cells"][2][0]["text"]["content"] == "Row 2, Cell 3"
    
    # Test with dictionary rows
    dict_rows = [
        {"header_1": "Value 1", "header_2": "Value 2", "header_3": "Value 3"},
        {"header_1": "Value 4", "header_2": "Value 5", "header_3": "Value 6"}
    ]
    
    block_with_dict_rows = create_table_block(headers, dict_rows)
    
    # Verify the block with dictionary rows
    assert block_with_dict_rows["type"] == "table"
    
    # Test with empty headers or rows
    assert create_table_block([], rows) is None
    assert create_table_block(headers, []) is None
    assert create_table_block(None, rows) is None
    assert create_table_block(headers, None) is None

def test_create_plant_content_blocks():
    """Test creating plant content blocks."""
    # Create a sample plant
    plant = {
        "Name": "Test Plant",
        "Image URL": "https://example.com/image.jpg",
        "Planting": {
            "content": "Planting instructions",
            "sub_headings": {
                "When to Plant": "Plant in spring"
            }
        },
        "Growing": {
            "content": "Growing instructions"
        },
        "Harvesting": {
            "content": "Harvesting instructions"
        },
        "Pests/Diseases": {
            "headers": ["Pest/Disease", "Type", "Symptoms", "Control"],
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
    
    # Create content blocks
    blocks = create_plant_content_blocks(plant)
    
    # Verify the blocks
    assert len(blocks) > 0
    
    # Check image block
    assert blocks[0]["type"] == "image"
    assert blocks[0]["image"]["external"]["url"] == "https://example.com/image.jpg"
    
    # Find planting section
    planting_heading_index = next(
        (i for i, block in enumerate(blocks) 
         if block["type"] == "heading_2" and 
         block["heading_2"]["rich_text"][0]["text"]["content"] == "Planting"),
        None
    )
    assert planting_heading_index is not None
    
    # Find recipes section
    recipes_heading_index = next(
        (i for i, block in enumerate(blocks) 
         if block["type"] == "heading_2" and 
         block["heading_2"]["rich_text"][0]["text"]["content"] == "Recipes"),
        None
    )
    assert recipes_heading_index is not None
    
    # Find pests and diseases section
    pests_heading_index = next(
        (i for i, block in enumerate(blocks) 
         if block["type"] == "heading_2" and 
         block["heading_2"]["rich_text"][0]["text"]["content"] == "Pests and Diseases"),
        None
    )
    assert pests_heading_index is not None
    
    # Find wit and wisdom section
    wisdom_heading_index = next(
        (i for i, block in enumerate(blocks) 
         if block["type"] == "heading_2" and 
         block["heading_2"]["rich_text"][0]["text"]["content"] == "Wit and Wisdom"),
        None
    )
    assert wisdom_heading_index is not None
    
    # Find cooking notes section
    cooking_heading_index = next(
        (i for i, block in enumerate(blocks) 
         if block["type"] == "heading_2" and 
         block["heading_2"]["rich_text"][0]["text"]["content"] == "Cooking Notes"),
        None
    )
    assert cooking_heading_index is not None
