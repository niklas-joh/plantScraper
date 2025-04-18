"""
Centralized configuration for the plant scraper project.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory for storing scraped data
DATA_DIR = os.path.join(BASE_DIR, "data")

# Output directory for storing processed data
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Base URL for scraping
BASE_URL = "https://www.almanac.com"
GRID_URL = f"{BASE_URL}/gardening/growing-guides"

# HTTP request headers to mimic a browser
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# Default GitHub repository information
GITHUB_OWNER = os.getenv("GITHUB_OWNER", "niklas-joh")
GITHUB_REPO = os.getenv("GITHUB_REPO", "plantScraper")

# Scraper settings
REQUEST_TIMEOUT = 10  # seconds
REQUEST_DELAY = 1  # seconds between requests
VERIFY_SSL = False  # Whether to verify SSL certificates

# File paths
PLANTS_CSV = os.path.join(DATA_DIR, "plants.csv")
PLANTS_DETAILED_JSON = os.path.join(OUTPUT_DIR, "plants_detailed.json")
