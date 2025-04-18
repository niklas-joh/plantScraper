"""
Tests for the config module.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config

def test_base_dir():
    """Test that BASE_DIR is set correctly."""
    expected_path = Path(__file__).resolve().parent.parent
    assert config.BASE_DIR == expected_path

def test_data_dir():
    """Test that DATA_DIR is set correctly."""
    expected_path = os.path.join(config.BASE_DIR, "data")
    assert config.DATA_DIR == expected_path

def test_output_dir():
    """Test that OUTPUT_DIR is set correctly."""
    expected_path = os.path.join(config.BASE_DIR, "output")
    assert config.OUTPUT_DIR == expected_path

def test_base_url():
    """Test that BASE_URL is set correctly."""
    assert config.BASE_URL == "https://www.almanac.com"

def test_grid_url():
    """Test that GRID_URL is set correctly."""
    assert config.GRID_URL == f"{config.BASE_URL}/gardening/growing-guides"

def test_http_headers():
    """Test that HTTP_HEADERS is set correctly."""
    assert "User-Agent" in config.HTTP_HEADERS
    assert isinstance(config.HTTP_HEADERS, dict)

def test_github_owner():
    """Test that GITHUB_OWNER is set correctly."""
    assert config.GITHUB_OWNER == os.getenv("GITHUB_OWNER", "niklas-joh")

def test_github_repo():
    """Test that GITHUB_REPO is set correctly."""
    assert config.GITHUB_REPO == os.getenv("GITHUB_REPO", "plantScraper")
