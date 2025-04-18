import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
import json
import time
import os
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def has_subheadings(item):
    """Check if a field item contains subheadings (h3 tags)."""
    if isinstance(item, str):
        return False  # String inputs cannot have h3 tags
    try:
        return len(item.find_all('h3')) > 0
    except AttributeError:
        return False  # Handle any other non-BeautifulSoup objects gracefully

def clean_content(content):
    """Clean the content by removing extra whitespace and newlines."""
    if not content:
        return ""
    # Remove extra whitespace and newlines
    content = ' '.join(content.split())
    return content.strip()

def save_html_to_file(content, filename):
    """Save HTML content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content.prettify())
    print(f"Content saved to {filename}")

def get_soup(url, headers):
    """Get BeautifulSoup object from URL."""
    response = requests.get(url, headers=headers, timeout=10, verify=False)
    if response.status_code != 200:
        print(f"  ⚠️ Skipped (Status {response.status_code})")
        return None
    return BeautifulSoup(response.content, "html.parser")

def process_table(table_tag):
    """Process a table tag and return formatted text."""
    table_data = []
    rows = table_tag.find_all('tr')
    for row in rows:
        row_data = []
        cells = row.find_all(['th', 'td'])
        for cell in cells:
            row_data.append(cell.get_text(strip=True))
        table_data.append(row_data)
    
    # Format table as text
    table_text = "\nTable:\n"
    for row in table_data:
        table_text += " | ".join(row) + "\n"
    return table_text

def extract_content_between_elements(start_elem, end_elem=None, stop_text=None, special_handling=None):
    """
    Extract content between two elements or until a specific text is found.
    
    Args:
        start_elem: The starting element
        end_elem: The ending element (optional)
        stop_text: Text to stop extraction at (optional)
        special_handling: Function to handle special elements (optional)
    
    Returns:
        Extracted content as string
    """
    if not start_elem:
        return ""
        
    content = []
    current_elem = start_elem.next_sibling
    
    while current_elem and (end_elem is None or current_elem != end_elem):
        if isinstance(current_elem, Tag):
            if current_elem.name != 'h3':  # Skip any nested h3
                if special_handling:
                    # Special handling returned content, use it
                    special_content, should_stop = special_handling(current_elem, "".join(content))
                    if special_content:
                        content.append(special_content)
                    if should_stop:
                        break
                else:
                    # Handle lists specially
                    if current_elem.name in ['ul', 'ol']:
                        for li in current_elem.find_all('li', recursive=True):
                            li_text = li.get_text(separator=" ", strip=True)
                            if li_text:
                                content.append("* " + li_text)  # Add bullet point for list items
                    else:
                        # Standard text extraction
                        text_content = current_elem.get_text(separator=" ", strip=True)
                        
                        # Check for stop text
                        if stop_text and stop_text in text_content:
                            stop_index = text_content.find(stop_text)
                            if stop_index > 0:
                                content.append(text_content[:stop_index].strip())
                            break
                        elif text_content:
                            content.append(text_content)
        
        current_elem = current_elem.next_sibling
        
        # If we've reached the end element, stop
        if end_elem is not None and current_elem == end_elem:
            break
    
    return " ".join(content).strip()

def handle_special_elements(elem, content):
    """Handle special elements like tables."""
    if elem.name == 'table':
        return process_table(elem), False
    return None, False

def extract_recipe_links(field_item):
    """Extract recipe links from a field item."""
    recipe_links = {}
    links = field_item.find_all('a')
    base_url = "https://www.almanac.com"
    
    for link in links:
        if '/recipe/' in link.get('href', ''):
            recipe_name = link.get_text(strip=True)
            recipe_url = base_url + link.get('href')
            recipe_links[recipe_name] = recipe_url
    
    return recipe_links

def process_field_with_subheadings(field_item, current_label):
    """Process a field item that contains subheadings (h3 tags)."""
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
            print(f"  Debug: {current_label} - Added subheading '{sub_heading}' with content length: {len(content_after_h3)}")
    
    return result

def clean_advertisement_content(content):
    """Remove ADVERTISEMENT text from content and clean up user questions in Cooking Notes."""
    if not isinstance(content, str):
        return content
        
    # Special handling for Cooking Notes section
    if "Artichokes are delicious raw or cooked" in content:  # This is a marker for Cooking Notes
        # Extract only the cooking instructions part
        cooking_instructions = content.split("Vegetables")[0].strip()
        return cooking_instructions
        
    # Handle variations of advertisement text
    ad_texts = ["ADVERTISEMENT", "Advertisement"]
    
    # First check if any ad text exists in the content
    has_ad = any(ad_text in content for ad_text in ad_texts)
    if not has_ad:
        return content
    
    # Split content by lines to handle multiple ad occurrences
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip lines that contain only advertisement text
        if any(line.strip() == ad_text for ad_text in ad_texts):
            continue
            
        # For lines that contain ad text mixed with content, truncate at the ad text
        ad_found = False
        for ad_text in ad_texts:
            if ad_text in line:
                ad_index = line.find(ad_text)
                if ad_index > 0:
                    cleaned_lines.append(line[:ad_index].strip())
                ad_found = True
                break
        
        # If no ad text in this line, keep it
        if not ad_found:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()

def process_plant_data(plant_data):
    processed_data = {}
    
    # Process each field
    for field_name, field_items in plant_data.items():
        print(f"  Processing content for: {field_name}")
        print(f"  Debug: HTML structure for {field_name}:")
        print(str(field_items[0])[:500] + "...")  # Print first 500 chars of HTML structure
        
        # Initialize content for this field
        field_content = ""
        sub_headings = {}
        
        # Special handling for fields that might have multiple items
        if field_name in ["Recipes"]:
            processed_data[field_name] = process_recipe_links(field_items)
            continue
            
        # Process each item in the field
        for item in field_items:
            # Clean the content
            content = clean_content(item)
            if not content:
                continue
                
            # Check if this field should be processed with subheadings
            if has_subheadings(item):
                print(f"  Debug: {field_name} - Found {len(item.find_all('h3'))} h3 tags")
                result = process_field_with_subheadings(item, field_name)
                
                # For fields that accumulate content (like Harvesting and Cooking Notes)
                if field_name in ["Harvesting", "Cooking Notes"]:
                    if not field_content:
                        field_content = result.get("content", "")
                    else:
                        field_content += "\n" + result.get("content", "")
                    
                    # Merge subheadings
                    sub_headings.update(result.get("sub_headings", {}))
                else:
                    field_content = result.get("content", "")
                    sub_headings = result.get("sub_headings", {})
            else:
                print(f"  Debug: {field_name} - Found 0 h3 tags")
                cleaned_content = clean_content(item)
                print(f"  Debug: {field_name} - No h3 tags, content length: {len(cleaned_content) if cleaned_content else 0}")
                
                # For fields that accumulate content
                if field_name in ["Harvesting", "Cooking Notes"]:
                    if cleaned_content:
                        if not field_content:
                            field_content = cleaned_content
                        else:
                            field_content += "\n" + cleaned_content
                else:
                    if cleaned_content:
                        field_content = cleaned_content
        
        # Clean advertisement content for all fields, especially Cooking Notes
        if isinstance(field_content, str):
            field_content = clean_advertisement_content(field_content)
        
        # Also clean advertisement content from all sub-headings
        if sub_headings:
            for heading, content in sub_headings.items():
                if isinstance(content, str):
                    sub_headings[heading] = clean_advertisement_content(content)
        
        print(f"  Content type for {field_name}: {type(field_content)}")
        print(f"  Content length: {len(field_content) if field_content else 0}")
        if sub_headings:
            print(f"  Sub-headings: {list(sub_headings.keys())}")
            processed_data[field_name] = {
                "content": field_content,
                "sub_headings": sub_headings
            }
        else:
            processed_data[field_name] = field_content
            
    return processed_data

def scrape_plant(row, index, total_count, headers):
    """Scrape details for a single plant."""
    try:
        name = row["Name"]
        link = row["Link"]
        image = row["Image URL"]
        plant_name = name.replace(" ", "_")

        print(f"[{index+1}/{total_count}] Scraping {name}...")

        # Get the soup
        soup = get_soup(link, headers)
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
        
        # Process each field's items
        for field_name, items in field_items.items():
            print(f"  Processing field: {field_name}")
            if not items:
                continue
                
            # Special handling for fields that might have multiple items
            if field_name == "Recipes":
                recipe_links = {}
                for item in items:
                    links = item.find_all('a')
                    for link in links:
                        if '/recipe/' in link.get('href', ''):
                            recipe_name = link.get_text(strip=True)
                            recipe_url = "https://www.almanac.com" + link.get('href')
                            recipe_links[recipe_name] = recipe_url
                if recipe_links:
                    plant_data[field_name] = recipe_links
                continue
            
            # Process field content
            field_content = ""
            sub_headings = {}
            
            for item in items:
                if has_subheadings(item):
                    result = process_field_with_subheadings(item, field_name)
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
                plant_data[field_name] = {
                    "content": field_content,
                    "sub_headings": sub_headings
                }
            else:
                plant_data[field_name] = field_content
        
        return plant_data
        
    except Exception as e:
        print(f"  ❌ Error processing {name}: {str(e)}")
        return None

def main():
    """Main function to run the scraper."""
    # Load the plants list
    try:
        df = pd.read_csv("plants.csv")
        print(f"Loaded {len(df)} plants from CSV file")
    except Exception as e:
        print(f"Error loading plants.csv: {str(e)}")
        return
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    all_plants = []
    total_count = len(df)
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    try:
        for index, row in df.head(1).iterrows():
            try:
                plant_data = scrape_plant(row, index, total_count, headers)
                if plant_data:
                    all_plants.append(plant_data)
                    # Save progress every 10 plants
                    if (index + 1) % 10 == 0:
                        with open("plants_detailed_with_h3.json", "w", encoding="utf-8") as f:
                            json.dump(all_plants, f, indent=2, ensure_ascii=False)
                        print(f"\n💾 Progress saved: {len(all_plants)}/{total_count} plants")
                
                time.sleep(1)  # Be polite to their servers
                
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
            with open("plants_detailed_with_h3.json", "w", encoding="utf-8") as f:
                json.dump(all_plants, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Done. Saved {len(all_plants)} plants to plants_detailed_with_h3.json")
        else:
            print("\n❌ No plants were successfully scraped")

if __name__ == "__main__":
    main()
