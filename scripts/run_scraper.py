#!/usr/bin/env python3
"""
Script to run the plant scraper.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.scraper.plant_list import PlantListScraper
from src.scraper.plant_details import PlantDetailsScraper
from src import config

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the plant scraper")
    parser.add_argument("--type", choices=["list", "details", "all"], default="all",
                        help="Type of scraper to run (list, details, or all)")
    parser.add_argument("--limit", type=int, help="Limit the number of plants to scrape")
    parser.add_argument("--output-dir", help="Output directory for scraped data")
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Set output directory if provided
    if args.output_dir:
        output_dir = args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        plants_csv = os.path.join(output_dir, "plants.csv")
        plants_json = os.path.join(output_dir, "plants_detailed.json")
    else:
        plants_csv = config.PLANTS_CSV
        plants_json = config.PLANTS_DETAILED_JSON
    
    # Run the plant list scraper
    if args.type in ["list", "all"]:
        print("\n=== Running Plant List Scraper ===\n")
        list_scraper = PlantListScraper()
        plants = list_scraper.scrape()
        
        if plants:
            list_scraper.save_to_csv(plants, plants_csv)
        else:
            print("❌ No plants were successfully scraped")
            if args.type == "all":
                print("Skipping details scraper since no plants were found")
                return
    
    # Run the plant details scraper
    if args.type in ["details", "all"]:
        print("\n=== Running Plant Details Scraper ===\n")
        details_scraper = PlantDetailsScraper(plants_csv=plants_csv)
        plants = details_scraper.scrape_all(limit=args.limit)
        
        if not plants:
            print("\n❌ No plant details were successfully scraped")

if __name__ == "__main__":
    main()
