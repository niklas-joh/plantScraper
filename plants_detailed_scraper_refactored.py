import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
import json
import time
import os

def save_html_to_file(content, filename):
    """Save HTML content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content.prettify())
    print(f"Content saved to {filename}")

def get_soup(url, headers):
    """Get BeautifulSoup object from URL."""
    response = requests.get(url, headers=headers, timeout=10)
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
    content = ""
    current_elem = start_elem.next_sibling
    
    while current_elem and (end_elem is None or current_elem != end_elem):
        if isinstance(current_elem, Tag):
            if current_elem.name != 'h3':  # Skip any nested h3
                if special_handling and special_handling(current_elem, content):
                    # Special handling returned content, use it
                    special_content, should_stop = special_handling(current_elem, content)
                    content += special_content
                    if should_stop:
                        break
                else:
                    # Standard text extraction
                    text_content = current_elem.get_text(separator=" ", strip=True)
                    
                    # Check for stop text
                    if stop_text and stop_text in text_content:
                        stop_index = text_content.find(stop_text)
                        if stop_index > 0:
                            content += " " + text_content[:stop_index].strip()
                        break
                    else:
                        content += " " + text_content
        
        current_elem = current_elem.next_sibling
        
        # If we've reached the end element, stop
        if end_elem is not None and current_elem == end_elem:
            break
    
    return content.strip()

def handle_special_elements(elem, content):
    """Handle special elements like tables."""
    if elem.name == 'table':
        return process_table(elem), False
    return None, False

def process_field_with_subheadings(field_item, current_label):
    """Process a field item that contains subheadings (h3 tags)."""
    result = {
        "content": "",
        "sub_headings": {}
    }
    
    # Find all h3 tags
    h3_tags = field_item.find_all('h3')
    
    if not h3_tags:
        # No h3 tags, just get the content
        result["content"] = field_item.get_text(separator=" ", strip=True)
        return result
    
    # Process content before the first h3 tag
    first_h3 = h3_tags[0]
    content_before_h3 = ""
    
    # Get content before the first h3
    for elem in first_h3.previous_siblings:
        if isinstance(elem, Tag):
            content_before_h3 = elem.get_text(separator=" ", strip=True) + " " + content_before_h3
    
    if content_before_h3.strip():
        result["content"] = content_before_h3.strip()
    
    # Process each h3 and its content
    for i, h3 in enumerate(h3_tags):
        sub_heading = h3.get_text(strip=True)
        
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
    name = row["Name"]
    link = row["Link"]
    image = row["Image URL"]
    plant_name = name.replace(" ", "_")

    print(f"[{index+1}/{total_count}] Scraping {name}...")

    try:
        # Get the soup
        soup = get_soup(link, headers)
        if not soup:
            return None
        
        # Save the first page for verification
        if index == 0:
            save_html_to_file(soup, "detailed_page.html")
        
        # Initialize plant data
        plant_data = {
            "Name": name,
            "Link": link,
            "Image URL": image
        }
        
        # Get the body wrapper
        body_wrapper = soup.select_one("div.field.field--name-field-body")
        
        # Save body wrapper content
        if body_wrapper:
            save_html_to_file(body_wrapper, f"body_wrapper_{plant_name}.html")
        else:
            print("Body wrapper not found")
            return None
        
        # Get content blocks
        content_blocks = soup.select("#block-almanaco-content")
        
        # Save content blocks
        if content_blocks:
            output_filename = f"content_blocks_{plant_name}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                for block in content_blocks:
                    f.write(block.prettify())
            print(f"Content blocks saved to {output_filename}")
        else:
            print("Content blocks not found")
            return None
        
        # Extract data from content blocks
        for block in content_blocks:
            current_label = None
            for child in block.descendants:
                if isinstance(child, Tag):
                    if 'field__label' in child.get('class', []):
                        current_label = child.get_text(strip=True)
                        # Initialize with a dictionary to hold both content and sub-headings
                        plant_data[current_label] = {
                            "content": "",
                            "sub_headings": {}
                        }
                    elif 'field__item' in child.get('class', []) and current_label:
                        # Process the field item
                        field_data = process_field_with_subheadings(child, current_label)
                        
                        # Update the plant data
                        if plant_data[current_label]["content"]:
                            plant_data[current_label]["content"] += f"\n{field_data['content']}"
                        else:
                            plant_data[current_label]["content"] = field_data["content"]
                        
                        # Add sub-headings
                        plant_data[current_label]["sub_headings"].update(field_data["sub_headings"])
        
        # Process the plant data
        return process_plant_data(plant_data)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
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
    for i, row in df.head(1).iterrows():
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
