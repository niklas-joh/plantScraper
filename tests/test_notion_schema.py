"""
Tests for the Notion schema module.

This module contains tests for the schema validation functions.
"""

import pytest
from src.notion.schema import validate_database_schema, get_database_creation_schema, PLANT_DATABASE_SCHEMA

def test_validate_database_schema():
    """Test validating a database schema."""
    # Create a valid database object
    valid_database = {
        "properties": {
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
        }
    }
    
    # Validate the schema
    is_valid, missing_properties = validate_database_schema(valid_database)
    
    # Verify the validation
    assert is_valid is True
    assert len(missing_properties) == 0
    
    # Create an invalid database object with missing properties
    invalid_database = {
        "properties": {
            "Name": {
                "title": {}
            },
            "Botanical Name": {
                "rich_text": {}
            }
            # Missing other properties
        }
    }
    
    # Validate the schema
    is_valid, missing_properties = validate_database_schema(invalid_database)
    
    # Verify the validation
    assert is_valid is False
    assert len(missing_properties) > 0
    assert "Plant Type" in missing_properties
    assert "Sun Exposure" in missing_properties
    
    # Create an invalid database object with wrong property types
    wrong_type_database = {
        "properties": {
            "Name": {
                "rich_text": {}  # Should be title
            },
            "Botanical Name": {
                "title": {}  # Should be rich_text
            },
            "Plant Type": {
                "multi_select": {}  # Should be select
            },
            "Sun Exposure": {
                "select": {}  # Should be multi_select
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
            }
        }
    }
    
    # Validate the schema
    is_valid, missing_properties = validate_database_schema(wrong_type_database)
    
    # Verify the validation
    assert is_valid is False
    assert len(missing_properties) > 0
    assert "Name" in missing_properties
    assert "Botanical Name" in missing_properties
    assert "Plant Type" in missing_properties
    assert "Sun Exposure" in missing_properties
    
    # Test with None or empty database
    is_valid, missing_properties = validate_database_schema(None)
    assert is_valid is False
    assert len(missing_properties) == len(PLANT_DATABASE_SCHEMA)
    
    is_valid, missing_properties = validate_database_schema({})
    assert is_valid is False
    assert len(missing_properties) == len(PLANT_DATABASE_SCHEMA)

def test_get_database_creation_schema():
    """Test getting the database creation schema."""
    # Get the schema
    schema = get_database_creation_schema()
    
    # Verify the schema
    assert schema is not None
    assert isinstance(schema, dict)
    assert "Name" in schema
    assert "title" in schema["Name"]
    assert "Botanical Name" in schema
    assert "rich_text" in schema["Botanical Name"]
    assert "Plant Type" in schema
    assert "select" in schema["Plant Type"]
    assert "Sun Exposure" in schema
    assert "multi_select" in schema["Sun Exposure"]
    assert "Soil pH" in schema
    assert "select" in schema["Soil pH"]
    assert "Bloom Time" in schema
    assert "multi_select" in schema["Bloom Time"]
    assert "Flower Color" in schema
    assert "multi_select" in schema["Flower Color"]
    assert "Hardiness Zone" in schema
    assert "multi_select" in schema["Hardiness Zone"]
    assert "Link" in schema
    assert "url" in schema["Link"]
    assert "Image URL" in schema
    assert "url" in schema["Image URL"]
    assert "Photo Credit" in schema
    assert "rich_text" in schema["Photo Credit"]
    
    # Verify the new fields
    assert "Planting" in schema
    assert "rich_text" in schema["Planting"]
    assert "Growing" in schema
    assert "rich_text" in schema["Growing"]
    assert "Harvesting" in schema
    assert "rich_text" in schema["Harvesting"]
    assert "Wit and Wisdom" in schema
    assert "rich_text" in schema["Wit and Wisdom"]
    assert "Cooking Notes" in schema
    assert "rich_text" in schema["Cooking Notes"]
