#!/usr/bin/env python3
"""
Demo script to show how tests would run in a real-world scenario.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config

def test_base_dir():
    """Test that BASE_DIR is set correctly."""
    expected_path = Path(__file__).resolve().parent.parent
    assert config.BASE_DIR == expected_path
    print("✅ test_base_dir: PASSED")

def test_data_dir():
    """Test that DATA_DIR is set correctly."""
    expected_path = os.path.join(config.BASE_DIR, "data")
    assert config.DATA_DIR == expected_path
    print("✅ test_data_dir: PASSED")

def test_output_dir():
    """Test that OUTPUT_DIR is set correctly."""
    expected_path = os.path.join(config.BASE_DIR, "output")
    assert config.OUTPUT_DIR == expected_path
    print("✅ test_output_dir: PASSED")

def test_base_url():
    """Test that BASE_URL is set correctly."""
    assert config.BASE_URL == "https://www.almanac.com"
    print("✅ test_base_url: PASSED")

def test_grid_url():
    """Test that GRID_URL is set correctly."""
    assert config.GRID_URL == f"{config.BASE_URL}/gardening/growing-guides"
    print("✅ test_grid_url: PASSED")

def test_http_headers():
    """Test that HTTP_HEADERS is set correctly."""
    assert "User-Agent" in config.HTTP_HEADERS
    assert isinstance(config.HTTP_HEADERS, dict)
    print("✅ test_http_headers: PASSED")

def test_github_owner():
    """Test that GITHUB_OWNER is set correctly."""
    assert config.GITHUB_OWNER == os.getenv("GITHUB_OWNER", "niklas-joh")
    print("✅ test_github_owner: PASSED")

def test_github_repo():
    """Test that GITHUB_REPO is set correctly."""
    assert config.GITHUB_REPO == os.getenv("GITHUB_REPO", "plantScraper")
    print("✅ test_github_repo: PASSED")

def main():
    """Run all tests."""
    print("\n=== Running Config Tests ===\n")
    
    # Run all tests
    test_base_dir()
    test_data_dir()
    test_output_dir()
    test_base_url()
    test_grid_url()
    test_http_headers()
    test_github_owner()
    test_github_repo()
    
    print("\n=== All Tests Passed ===\n")
    print("In a real-world scenario with pytest installed, you would run:")
    print("pytest tests/test_config.py -v")
    print("\nThis would run all the tests in the test_config.py file and provide verbose output.")

if __name__ == "__main__":
    main()
