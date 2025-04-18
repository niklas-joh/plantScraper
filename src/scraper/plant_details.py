"""
Plant details scraper for extracting detailed plant information.
"""

import os
import time
import json
from bs4 import Tag
from src.scraper.base import BaseScraper, extract_content_between_elements, handle_special_elements
from src.processors.content_cleaner import (
    clean_content, 
    clean_advertisement_content, 
    has_subheadings,
    extract_recipe_links
)
from src.utils.file_io import load_from_csv, save_to_json
from src import config

class PlantDetailsScraper(BaseScraper):
    """Scraper for extracting detailed plant information."""
    
    def __init__(self, plants_csv=None, **kwargs):
        """
        Initialize the plant details scraper.
        
        Args:
            plants_csv (str, optional): Path to the CSV file with plant list. Defaults to config.PLANTS_CSV.
            **kwargs: Additional arguments to pass to BaseScraper.
        """
        super().__init__(**kwargs)
        self.plants_csv = plants_csv or config.PLANTS_CSV
    
    def scrape_all(self, limit=None):
        """
        Scrape details for all plants in the CSV file.
        
        Args:
            limit (int, optional): Maximum number of plants to scrape. Defaults to None (all plants).
            
        Returns:
            list: List of plant details dictionaries
        """
        # Load the plants list
        df = load_from_csv(self.plants_csv)
        if df is None:
            return None
        
        # Limit the number of plants if specified
        if limit:
            df = df.head(limit)
        
        all_plants = []
        total_count = len(df)
        
        try:
            for index, row in df.iterrows():
                try:
                    plant_data = self.scrape_plant(row, index, total_count)
                    if plant_data:
                        all_plants.append(plant_data)
                        # Save progress every 10 plants
                        if (index + 1) % 10 == 0:
                            self.save_progress(all_plants)
                    
                    self.sleep()  # Be polite to their servers
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"\n⚠️ Error processing plant at index {index}: {str(e)}")
                    continue
            
        except KeyboardInterrupt:
            print("\n⚠️ Scraping interrupted by user. Saving progress...")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        finally:
            # Final save
            if all_plants:
                self.save_progress(all_plants)
        
        return all_plants
    
    def scrape_plant(self, row, index, total_count):
        """
        Scrape details for a single plant.
        
        Args:
            row: DataFrame row with plant basic information
            index: Index of the plant in the DataFrame
            total_count: Total number of plants
            
        Returns:
            dict: Plant details dictionary or None if scraping failed
        """
        try:
            name = row["Name"]
            link = row["Link"]
            image = row["Image URL"]
            plant_name = name.replace(" ", "_")

            print(f"[{index+1}/{total_count}] Scraping {name}...")

            # Get the soup
            soup = self.get_soup(link)
            if not soup:
                print(f"  ⚠️ Failed to get soup for {name}")
                return None
            
            # Initialize plant data with basic fields
            plant_data = {
                "Name": name,
                "Link": link,
                "Image URL": image
            }
            
            # Get content blocks
            content_blocks = soup.select("#block-almanaco-content")
            if not content_blocks:
                print(f"  ⚠️ No content blocks found for {name}")
                return None
                
            # Extract data from content blocks
            field_items = {}  # Collect all field items first
            current_label = None
            
            for block in content_blocks:
                for child in block.descendants:
                    if isinstance(child, Tag):
                        if 'field__label' in child.get('class', []):
                            current_label = child.get_text(strip=True)
                            if current_label and current_label not in ["Name", "Link", "Image URL"]:  # Skip basic fields
                                field_items[current_label] = []
                        elif current_label and 'field__item' in child.get('class', []):
                            if current_label not in ["Name", "Link", "Image URL"]:  # Skip basic fields
                                field_items[current_label].append(child)
            
            # Process the field items
            processed_data = self.process_field_items(field_items)
            plant_data.update(processed_data)
            
            return plant_data
            
        except Exception as e:
            print(f"  ❌ Error processing {name}: {str(e)}")
            return None
    
    def process_field_items(self, field_items):
        """
        Process field items extracted from the plant page.
        
        Args:
            field_items (dict): Dictionary mapping field names to lists of field items
            
        Returns:
            dict: Processed field data
        """
        processed_data = {}
        
        # Process each field
        for field_name, items in field_items.items():
            print(f"  Processing field: {field_name}")
            if not items:
                continue
                
            # Special handling for fields that might have multiple items
            if field_name == "Recipes":
                recipe_links = {}
                for item in items:
                    links = extract_recipe_links(item)
                    recipe_links.update(links)
                if recipe_links:
                    processed_data[field_name] = recipe_links
                continue
            
            # Special handling for Pests/Diseases section to preserve table structure
            if field_name == "Pests/Diseases":
                for item in items:
                    # Look for tables in the item
                    tables = item.find_all('table')
                    if tables:
                        # Process the first table found
                        from src.scraper.base import process_table
                        table_data = process_table(tables[0])
                        processed_data[field_name] = table_data
                        break
                # If we processed a table, continue to next field
                if field_name in processed_data:
                    continue
            
            # Process field content
            field_content = ""
            sub_headings = {}
            
            for item in items:
                if has_subheadings(item):
                    result = self.process_field_with_subheadings(item, field_name)
                    if isinstance(result, dict):
                        if not field_content and "content" in result:
                            field_content = result["content"]
                        elif "content" in result:
                            field_content += "\n" + result["content"]
                        
                        if "sub_headings" in result:
                            sub_headings.update(result["sub_headings"])
                else:
                    content = clean_content(item.get_text(separator=" ", strip=True))
                    if content:
                        if not field_content:
                            field_content = content
                        else:
                            field_content += "\n" + content
            
            # Clean advertisement content before storing
            if isinstance(field_content, str):
                field_content = clean_advertisement_content(field_content)
            
            # Also clean advertisement content from all sub-headings
            if sub_headings:
                for heading, content in sub_headings.items():
                    if isinstance(content, str):
                        sub_headings[heading] = clean_advertisement_content(content)
            
            # Store the processed content
            if sub_headings:
                processed_data[field_name] = {
                    "content": field_content,
                    "sub_headings": sub_headings
                }
            else:
                processed_data[field_name] = field_content
        
        return processed_data
    
    def process_field_with_subheadings(self, field_item, current_label):
        """
        Process a field item that contains subheadings (h3 tags).
        
        Args:
            field_item: BeautifulSoup element containing the field item
            current_label: Name of the current field
            
        Returns:
            dict: Dictionary with content and sub_headings
        """
        if not field_item:
            print(f"  Debug: {current_label} - field_item is None")
            return {"content": "", "sub_headings": {}}
            
        result = {
            "content": "",
            "sub_headings": {}
        }
        
        # Special handling for Recipes section
        if current_label == "Recipes":
            recipe_links = extract_recipe_links(field_item)
            if recipe_links:
                return recipe_links
            # If no recipe links found, fall back to text content
            result["content"] = field_item.get_text(separator=" ", strip=True) or ""
            return result
        
        # Find all h3 tags
        h3_tags = field_item.find_all('h3')
        print(f"  Debug: {current_label} - Found {len(h3_tags)} h3 tags")
        
        if not h3_tags:
            # No h3 tags, get all text content including lists
            content_parts = []
            for elem in field_item.children:
                if isinstance(elem, Tag):
                    # Handle lists specially
                    if elem.name in ['ul', 'ol']:
                        for li in elem.find_all('li', recursive=True):
                            content_parts.append(li.get_text(strip=True))
                    else:
                        text = elem.get_text(separator=" ", strip=True)
                        if text:
                            content_parts.append(text)
            
            result["content"] = " ".join(content_parts)
            print(f"  Debug: {current_label} - No h3 tags, content length: {len(result['content'])}")
            return result
        
        # Process content before the first h3 tag
        first_h3 = h3_tags[0]
        content_before_h3 = []
        
        # Get content before the first h3, including lists
        for elem in first_h3.previous_siblings:
            if isinstance(elem, Tag):
                if elem.name in ['ul', 'ol']:
                    for li in elem.find_all('li', recursive=True):
                        content_before_h3.insert(0, li.get_text(strip=True))
                else:
                    text = elem.get_text(separator=" ", strip=True)
                    if text:
                        content_before_h3.insert(0, text)
        
        if content_before_h3:
            result["content"] = " ".join(content_before_h3)
            print(f"  Debug: {current_label} - Content before h3 length: {len(result['content'])}")
        
        # Process each h3 and its content
        for i, h3 in enumerate(h3_tags):
            sub_heading = h3.get_text(strip=True)
            if not sub_heading:
                print(f"  Debug: {current_label} - Empty subheading at index {i}")
                continue
                
            # Determine special handling based on the label
            stop_text = "ADVERTISEMENT" if current_label == "Cooking Notes" else None
            special_handler = handle_special_elements if current_label == "Pests/Diseases" else None
            
            # Get the next h3 if it exists
            next_h3 = h3_tags[i + 1] if i < len(h3_tags) - 1 else None
            
            # Extract content between this h3 and the next h3 (or end)
            content_after_h3 = extract_content_between_elements(
                h3, 
                next_h3, 
                stop_text=stop_text,
                special_handling=special_handler
            )
            
            if content_after_h3:
                result["sub_headings"][sub_heading] = content_after_h3
                print(f"  Debug: {current_label} - Added subheading '{sub_heading}' with content length: {len(str(content_after_h3))}")
        
        return result
    
    def save_progress(self, plants, filepath=None):
        """
        Save progress to a JSON file.
        
        Args:
            plants (list): List of plant details dictionaries
            filepath (str, optional): Path to save the JSON file. Defaults to config.PLANTS_DETAILED_JSON.
            
        Returns:
            bool: True if successful, False otherwise
        """
        filepath = filepath or config.PLANTS_DETAILED_JSON
        result = save_to_json(plants, filepath)
        if result:
            print(f"\n💾 Progress saved: {len(plants)} plants")
        return result

def main():
    """Main function to run the scraper."""
    scraper = PlantDetailsScraper()
    plants = scraper.scrape_all(limit=1)  # Limit to 1 plant for testing
    
    if not plants:
        print("\n❌ No plants were successfully scraped")

if __name__ == "__main__":
    main()
