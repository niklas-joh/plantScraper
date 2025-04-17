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
    
    if not h3_tags:
        # No h3 tags, just get the content
        result["content"] = field_item.get_text(separator=" ", strip=True) or ""
        return result
    
    # Process content before the first h3 tag
    first_h3 = h3_tags[0]
    content_before_h3 = []
    
    # Get content before the first h3
    for elem in first_h3.previous_siblings:
        if isinstance(elem, Tag):
            text = elem.get_text(separator=" ", strip=True)
            if text:
                content_before_h3.insert(0, text)
    
    if content_before_h3:
        result["content"] = " ".join(content_before_h3)
    
    # Process each h3 and its content
    for i, h3 in enumerate(h3_tags):
        sub_heading = h3.get_text(strip=True)
        if not sub_heading:
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
    
    return result

def clean_advertisement_content(content):
    """Remove ADVERTISEMENT text from content."""
    if isinstance(content, str) and "ADVERTISEMENT" in content:
        ad_index = content.find("ADVERTISEMENT")
        if ad_index > 0:
            return content[:ad_index].strip()
    return content

def process_plant_data(plant_data):
    """Process the plant data to finalize the structure."""
    processed_data = {}
    
    for key, value in plant_data.items():
        # Handle recipe links (dictionary of recipe name to URL)
        if key == "Recipes" and isinstance(value, dict) and all(isinstance(v, str) for v in value.values()):
            processed_data[key] = value
            continue
            
        # Check if this is one of our structured fields with sub-headings
        if isinstance(value, dict) and "content" in value and "sub_headings" in value:
            # Special handling for Cooking Notes to stop at ADVERTISEMENT
            if key == "Cooking Notes":
                value["content"] = clean_advertisement_content(value["content"])
                
                # Clean sub_headings
                for sub_key in value["sub_headings"]:
                    value["sub_headings"][sub_key] = clean_advertisement_content(value["sub_headings"][sub_key])
            
            # If there are sub-headings, keep the structured format
            if value["sub_headings"]:
                # Extract all paragraphs from the content
                if value["content"]:
                    paragraphs = value["content"].split("\n")
                    
                    # Keep track of which paragraphs are duplicated in subheadings
                    duplicate_paragraphs = set()
                    
                    # Check each paragraph against each subheading content
                    for i, paragraph in enumerate(paragraphs):
                        for sub_heading, sub_content in value["sub_headings"].items():
                            # If the paragraph is in the subheading content, mark it as duplicate
                            if paragraph.strip() and paragraph.strip() in sub_content:
                                duplicate_paragraphs.add(i)
                    
                    # Build new content with only non-duplicate paragraphs
                    new_paragraphs = []
                    for i, paragraph in enumerate(paragraphs):
                        if i not in duplicate_paragraphs and paragraph.strip():
                            new_paragraphs.append(paragraph)
                    
                    # If we have any non-duplicate paragraphs, join them back together
                    if new_paragraphs:
                        value["content"] = "\n".join(new_paragraphs)
                    else:
                        value["content"] = None
                
                processed_data[key] = value
            else:
                # If no sub-headings, just use the content directly
                processed_data[key] = value["content"]
        else:
            # For simple fields, just copy the value
            processed_data[key] = value
    
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
        
        # Initialize plant data
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
        for block in content_blocks:
            current_label = None
            for child in block.descendants:
                if isinstance(child, Tag):
                    if 'field__label' in child.get('class', []):
                        current_label = child.get_text(strip=True)
                        if current_label:
                            # Initialize with a dictionary to hold both content and sub-headings
                            plant_data[current_label] = {
                                "content": "",
                                "sub_headings": {}
                            }
                    elif current_label and 'field__item' in child.get('class', []):
                        # Process the field item
                        field_data = process_field_with_subheadings(child, current_label)
                        if field_data:
                            plant_data[current_label] = field_data
        
        return process_plant_data(plant_data)
        
    except Exception as e:
        print(f"  ❌ Error processing {name}: {str(e)}")
        return None

def main():
    """Main function to run the scraper."""
    # Load the plants list
    df = pd.read_csv("plants.csv")
    base_url = "https://www.almanac.com"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    all_plants = []
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Scrape each plant
    for i, row in df.iterrows():
        plant_data = scrape_plant(row, i, len(df), headers)
        if plant_data:
            all_plants.append(plant_data)
        
        time.sleep(0.5)  # Be polite to their servers
    
    # Save to JSON
    with open("plants_detailed_with_h3.json", "w", encoding="utf-8") as f:
        json.dump(all_plants, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Done. Saved {len(all_plants)} plants to plants_detailed_with_h3.json")

if __name__ == "__main__":
    main()
