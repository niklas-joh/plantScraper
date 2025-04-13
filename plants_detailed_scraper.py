import requests
from bs4 import BeautifulSoup
from bs4 import Tag
import pandas as pd
import json
import time

# Load your original plants list
df = pd.read_csv("plants.csv")
base_url = "https://www.almanac.com"

all_plants = []

headers = {
    "User-Agent": "Mozilla/5.0"
}
for i, row in df.head(1).iterrows():
    name = row["Name"]
    link = row["Link"]
    image = row["Image URL"]

    print(f"[{i+1}/{len(df)}] Scraping {name}...")

    try:
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"  ⚠️ Skipped (Status {response.status_code})")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
    
        # Write page HTML to a file to verify scraping worked
        if i == 0:
            with open("detailed_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            
        content_blocks = soup.select("#block-almanaco-content")

        plant_data = {
            "Name": name,
            "Link": link,
            "Image URL": image
        }

        # ✅ Select the correct container
        body_wrapper = soup.select_one("div.field.field--name-field-body")
        plant_name = name.replace(" ", "_")

        # Save body_wrapper content to a file
        if body_wrapper:            
            output_filename = f"body_wrapper_{plant_name}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(body_wrapper.prettify())
            print(f"Body wrapper content saved to {output_filename}")
        else:
            print("Body wrapper not found")
        
        if not body_wrapper:
            print("  ⚠️ Could not find body content")
            continue

        # Save content_blocks content to a file
        if content_blocks:
            output_filename = f"content_blocks_{plant_name}.html"
            with open(output_filename, 'w', encoding='utf-8') as f:
                for block in content_blocks:
                    f.write(block.prettify())
            print(f"Content blocks saved to {output_filename}")
        else:
            print("Content blocks not found")
            continue

        # Extract data from the content blocks 
        # Initialize plant data dictionary
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
                        # Process the field item content, looking for h3 tags
                        current_sub_heading = None
                        
                        # First, check if there are h3 tags in this field item
                        h3_tags = child.find_all('h3')
                        
                        if h3_tags:  # If there are h3 tags, process content by sections
                            # Get a copy of the field item to extract content before the first h3
                            field_item_copy = child.prettify()
                            
                            # Process content before the first h3 tag
                            first_h3 = h3_tags[0]
                            content_before_h3 = ""
                            
                            # Get content before the first h3
                            for elem in first_h3.previous_siblings:
                                if isinstance(elem, Tag):
                                    content_before_h3 = elem.get_text(separator=" ", strip=True) + " " + content_before_h3
                            
                            if content_before_h3.strip():
                                if plant_data[current_label]["content"]:
                                    plant_data[current_label]["content"] += f"\n{content_before_h3.strip()}"
                                else:
                                    plant_data[current_label]["content"] = content_before_h3.strip()
                            
                            # Process each h3 and its content
                            for i, h3 in enumerate(h3_tags):
                                sub_heading = h3.get_text(strip=True)
                                plant_data[current_label]["sub_headings"][sub_heading] = ""
                                
                                # Get content after this h3 and before the next h3 (if any)
                                content_after_h3 = ""
                                current_elem = h3.next_sibling
                                
                                # Check if this is the "Cooking Notes" section and we need to stop at "ADVERTISEMENT"
                                if current_label == "Cooking Notes":
                                    # If this is the last h3, get all content after it until "ADVERTISEMENT"
                                    if i == len(h3_tags) - 1:
                                        found_ad = False
                                        while current_elem and not found_ad:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name != 'h3':  # Skip any nested h3
                                                    text_content = current_elem.get_text(separator=" ", strip=True)
                                                    if "ADVERTISEMENT" in text_content:
                                                        # Stop at ADVERTISEMENT
                                                        ad_index = text_content.find("ADVERTISEMENT")
                                                        if ad_index > 0:
                                                            content_after_h3 += " " + text_content[:ad_index].strip()
                                                        found_ad = True
                                                        break
                                                    else:
                                                        content_after_h3 += " " + text_content
                                            current_elem = current_elem.next_sibling
                                    else:
                                        # Get content until the next h3 or until "ADVERTISEMENT"
                                        next_h3 = h3_tags[i + 1]
                                        found_ad = False
                                        while current_elem and current_elem != next_h3 and not found_ad:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name != 'h3':  # Skip any nested h3
                                                    text_content = current_elem.get_text(separator=" ", strip=True)
                                                    if "ADVERTISEMENT" in text_content:
                                                        # Stop at ADVERTISEMENT
                                                        ad_index = text_content.find("ADVERTISEMENT")
                                                        if ad_index > 0:
                                                            content_after_h3 += " " + text_content[:ad_index].strip()
                                                        found_ad = True
                                                        break
                                                    else:
                                                        content_after_h3 += " " + text_content
                                            current_elem = current_elem.next_sibling
                                # For Pests/Diseases section, check for tables and preserve them
                                elif current_label == "Pests/Diseases":
                                    # If this is the last h3, get all content after it
                                    if i == len(h3_tags) - 1:
                                        while current_elem:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name == 'table':
                                                    # Process table structure
                                                    table_data = []
                                                    rows = current_elem.find_all('tr')
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
                                                    content_after_h3 += table_text
                                                elif current_elem.name != 'h3':  # Skip any nested h3
                                                    content_after_h3 += " " + current_elem.get_text(separator=" ", strip=True)
                                            current_elem = current_elem.next_sibling
                                    else:
                                        # Get content until the next h3
                                        next_h3 = h3_tags[i + 1]
                                        while current_elem and current_elem != next_h3:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name == 'table':
                                                    # Process table structure
                                                    table_data = []
                                                    rows = current_elem.find_all('tr')
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
                                                    content_after_h3 += table_text
                                                elif current_elem.name != 'h3':  # Skip any nested h3
                                                    content_after_h3 += " " + current_elem.get_text(separator=" ", strip=True)
                                            current_elem = current_elem.next_sibling
                                else:
                                    # Standard processing for other sections
                                    # If this is the last h3, get all content after it
                                    if i == len(h3_tags) - 1:
                                        while current_elem:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name != 'h3':  # Skip any nested h3
                                                    content_after_h3 += " " + current_elem.get_text(separator=" ", strip=True)
                                            current_elem = current_elem.next_sibling
                                    else:
                                        # Get content until the next h3
                                        next_h3 = h3_tags[i + 1]
                                        while current_elem and current_elem != next_h3:
                                            if isinstance(current_elem, Tag):
                                                if current_elem.name != 'h3':  # Skip any nested h3
                                                    content_after_h3 += " " + current_elem.get_text(separator=" ", strip=True)
                                            current_elem = current_elem.next_sibling
                                
                                plant_data[current_label]["sub_headings"][sub_heading] = content_after_h3.strip()
                            
                            # For sections with subheadings, don't add the entire content to the content field
                            # This avoids duplication
                        else:
                            # No h3 tags, just add the content normally
                            content = child.get_text(separator=" ", strip=True)
                            if plant_data[current_label]["content"]:
                                plant_data[current_label]["content"] += f"\n{content}"
                            else:
                                plant_data[current_label]["content"] = f"{content}"

        # Process the plant data to convert simple fields to their original format
        # and keep the structured format for fields with h3 headings
        processed_plant_data = {}
        for key, value in plant_data.items():
            # Check if this is one of our structured fields with sub-headings
            if isinstance(value, dict) and "content" in value and "sub_headings" in value:
                # Special handling for Cooking Notes to stop at ADVERTISEMENT
                if key == "Cooking Notes":
                    # Check content for ADVERTISEMENT
                    if "ADVERTISEMENT" in value["content"]:
                        ad_index = value["content"].find("ADVERTISEMENT")
                        if ad_index > 0:
                            value["content"] = value["content"][:ad_index].strip()
                    
                    # Check sub_headings for ADVERTISEMENT
                    for sub_key in value["sub_headings"]:
                        if "ADVERTISEMENT" in value["sub_headings"][sub_key]:
                            ad_index = value["sub_headings"][sub_key].find("ADVERTISEMENT")
                            if ad_index > 0:
                                value["sub_headings"][sub_key] = value["sub_headings"][sub_key][:ad_index].strip()
                
                # If there are sub-headings, keep the structured format
                if value["sub_headings"]:
                    # For sections with subheadings, we need to extract the content that's not in subheadings
                    
                    # First, get all the content from the field item
                    original_content = value["content"]
                    
                    # Check if the content is duplicated in the subheadings
                    # We'll use a more careful approach to avoid losing unique content
                    
                    # Extract all paragraphs from the content
                    paragraphs = original_content.split("\n")
                    
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
                        
                    processed_plant_data[key] = value
                else:
                    # If no sub-headings, just use the content directly
                    processed_plant_data[key] = value["content"]
            else:
                # For simple fields, just copy the value
                processed_plant_data[key] = value
                
        # Save plant data
        all_plants.append(processed_plant_data)
        # print(json.dumps(processed_plant_data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"  ❌ Error: {e}")

    time.sleep(0.5)  # Be polite to their servers

# Save to JSON
with open("plants_detailed_with_h3.json", "w", encoding="utf-8") as f:
    json.dump(all_plants, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done. Saved {len(all_plants)} plants to plants_detailed_with_h3.json")
