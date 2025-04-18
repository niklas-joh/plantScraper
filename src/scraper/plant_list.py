"""
Plant list scraper for extracting basic plant information.
"""

from bs4 import BeautifulSoup
import pandas as pd
from src.scraper.base import BaseScraper
from src.utils.file_io import save_to_csv
from src import config

class PlantListScraper(BaseScraper):
    """Scraper for extracting basic plant information from the grid page."""
    
    def __init__(self, url=None, **kwargs):
        """
        Initialize the plant list scraper.
        
        Args:
            url (str, optional): URL to scrape. Defaults to config.GRID_URL.
            **kwargs: Additional arguments to pass to BaseScraper.
        """
        super().__init__(**kwargs)
        self.url = url or config.GRID_URL
    
    def scrape(self):
        """
        Scrape the plant list page.
        
        Returns:
            list: List of plant dictionaries or None if scraping failed
        """
        print(f"Scraping plant list from {self.url}")
        
        # Get the soup
        soup = self.get_soup(self.url)
        if not soup:
            print(f"❌ Failed to get soup for {self.url}")
            return None
        
        # Extract plant items
        plants = []
        plant_items = soup.select("div.views-view-grid__item")
        print(f"Found {len(plant_items)} plant items")
        
        for item in plant_items:
            plant_data = self._extract_plant_data(item)
            if plant_data:
                plants.append(plant_data)
        
        print(f"✅ Extracted data for {len(plants)} plants")
        return plants
    
    def _extract_plant_data(self, item):
        """
        Extract data from a plant item.
        
        Args:
            item: BeautifulSoup element representing a plant item
            
        Returns:
            dict: Plant data dictionary or None if extraction failed
        """
        title_elem = item.select_one("h3 a")
        if not title_elem:
            return None
        
        name = title_elem.text.strip()
        link = config.BASE_URL + title_elem["href"]
        
        # Get image URL
        img_elem = item.select_one("img")
        img_path = img_elem.get("src") or img_elem.get("data-src", "") if img_elem else ""
        img_url = config.BASE_URL + img_path if img_path.startswith("/") else img_path
        
        return {
            "Name": name,
            "Link": link,
            "Image URL": img_url
        }
    
    def save_to_csv(self, plants, filepath=None):
        """
        Save plants to CSV.
        
        Args:
            plants (list): List of plant dictionaries
            filepath (str, optional): Path to save the CSV file. Defaults to config.PLANTS_CSV.
            
        Returns:
            bool: True if successful, False otherwise
        """
        return save_to_csv(plants, filepath)

def main():
    """Main function to run the scraper."""
    scraper = PlantListScraper()
    plants = scraper.scrape()
    
    if plants:
        scraper.save_to_csv(plants)
    else:
        print("❌ No plants were successfully scraped")

if __name__ == "__main__":
    main()
