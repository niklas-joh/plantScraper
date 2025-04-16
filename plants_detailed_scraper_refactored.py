import urllib.request
import html.parser
import csv
import json
import time
import os
import ssl

# Create an SSL context that doesn't verify certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class PlantHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset_state()

    def reset_state(self):
        """Reset the parser state."""
        self.data = []
        self.current_tag = None
        self.current_attrs = None
        self.recording = False
        self.current_data = []
        self.in_target_div = False
        self.field_label = None
        self.field_items = []
        self.in_field_label = False
        self.in_field_item = False
        self.current_field = {"label": None, "content": []}
        self.fields = []
        self.in_content = False
        self.in_article = False
        self.in_text_content = False
        self.current_section = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get('class', '').split()

        # Track when we're in a text content section
        if 'text-content' in classes and 'field' in classes:
            self.in_text_content = True
            # Look for specific field names
            if 'field--name-field-planting' in classes:
                self.current_section = "Planting"
            elif 'field--name-field-care' in classes:
                self.current_section = "Growing"
            elif 'field--name-field-harvest' in classes:
                self.current_section = "Harvesting"
            elif 'field--name-field__recommended' in classes:
                self.current_section = "Varieties"
            elif 'field--name-field-body' in classes:
                self.current_section = "About"
            return

        # Start recording content when we're in a field item
        if self.in_text_content and 'field__item' in classes:
            self.in_field_item = True
            self.recording = True
            self.current_data = []  # Reset current data for new section
            return

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.in_text_content and self.current_section:
                self.in_text_content = False
                if self.current_data:  # If we have content
                    content = ' '.join(''.join(self.current_data).split())  # Clean up whitespace
                    if content:  # Only add non-empty content
                        self.fields.append({
                            "label": self.current_section,
                            "content": [content]
                        })
                self.current_section = None
                self.current_data = []
            elif self.in_field_item:
                self.in_field_item = False
                self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.current_data.append(data.strip())

def save_html_to_file(content, filename):
    """Save HTML content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Content saved to {filename}")

def get_html(url, headers):
    """Get HTML content from URL."""
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, context=ssl_context, timeout=10) as response:
            if response.status != 200:
                print(f"  ⚠️ Skipped (Status {response.status})")
                return None
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"  ⚠️ Error: {str(e)}")
        return None

def process_table(table_html):
    """Process a table and return formatted text."""
    parser = PlantHTMLParser()
    parser.feed(table_html)
    
    # Format table as text
    table_text = "\nTable:\n"
    current_row = []
    for cell in parser.data:
        current_row.append(cell)
        if len(current_row) == 2:  # Assuming 2 columns
            table_text += " | ".join(current_row) + "\n"
            current_row = []
    return table_text

def extract_content_between_elements(html_content, start_tag, end_tag=None, stop_text=None):
    """Extract content between two elements or until specific text is found."""
    parser = PlantHTMLParser()
    parser.feed(html_content)
    return ' '.join(parser.current_data).strip()

def handle_special_elements(html_content):
    """Handle special elements like tables."""
    if '<table' in html_content.lower():
        return process_table(html_content), False
    return None, False

def process_field_with_subheadings(field_html, current_label):
    """Process a field that contains subheadings (h3 tags)."""
    result = {
        "content": field_html,
        "sub_headings": {}
    }
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
        if isinstance(value, dict) and "content" in value and "sub_headings" in value:
            if key == "Cooking Notes":
                value["content"] = clean_advertisement_content(value["content"])
                for sub_key in value["sub_headings"]:
                    value["sub_headings"][sub_key] = clean_advertisement_content(value["sub_headings"][sub_key])
            processed_data[key] = value["content"]
        else:
            processed_data[key] = value
    
    return processed_data

def scrape_plant(row, index, total_count, headers):
    """Scrape details for a single plant."""
    name = row[0]  # Name is the first column
    link = row[1]  # Link is the second column
    image = row[2]  # Image URL is the third column
    plant_name = name.replace(" ", "_")

    print(f"\n[{index+1}/{total_count}] Scraping {name}...")
    print(f"URL: {link}")

    try:
        # Get the HTML content
        html_content = get_html(link, headers)
        if not html_content:
            return None
        
        # Save the first page for verification
        if index == 0:
            save_html_to_file(html_content, "detailed_page.html")
        
        # Initialize plant data
        plant_data = {
            "Name": name,
            "Link": link,
            "Image URL": image
        }
        
        # Create parser for the page
        parser = PlantHTMLParser()
        parser.feed(html_content)
        
        print("\nExtracting sections:")
        # Process the extracted fields
        for field in parser.fields:
            label = field["label"]
            content = "\n".join(field["content"])
            
            # Clean up the content
            content = content.strip()
            if content:
                print(f"Found section: {label}")
                if label == "Planting":
                    plant_data["Planting Information"] = content
                elif label == "Growing":
                    plant_data["Growing Information"] = content
                elif label == "Varieties":
                    plant_data["Varieties"] = content
                elif label == "Harvesting":
                    plant_data["Harvesting Information"] = content
                elif label == "Photo Credit":
                    plant_data["Photo Credit"] = content
                else:
                    # Store any other fields we find
                    plant_data[label] = content
        
        processed_data = process_plant_data(plant_data)
        print(f"\nTotal fields captured: {len(processed_data)}")
        print("Field names:", ", ".join(processed_data.keys()))
        
        return processed_data
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def main():
    """Main function to run the scraper."""
    # Load the plants list from CSV
    plants = []
    try:
        with open("plants.csv", 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            next(csv_reader)  # Skip header row
            plants = list(csv_reader)
    except FileNotFoundError:
        print("Error: plants.csv file not found!")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    all_plants = []
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    print(f"Found {len(plants)} plants in CSV file")
    print("Testing with first plant only...")
    
    # Process only the first plant for testing
    for i, row in enumerate(plants[:1]):  # Only process first plant for testing
        plant_data = scrape_plant(row, i, 1, headers)
        if plant_data:
            all_plants.append(plant_data)
            # Save progress after each successful scrape
            output_file = "plants_detailed_with_h3.json"
            with open(output_file, "w", encoding='utf-8') as f:
                json.dump(all_plants, f, indent=2, ensure_ascii=False)
            print(f"✓ Progress saved: {len(all_plants)}/1 plants processed")
        
        time.sleep(1)  # Be polite to their servers
    
    print(f"\n✅ Done. Saved test data to plants_detailed_with_h3.json")
    print("Please check the output for completeness before processing all plants.")

if __name__ == "__main__":
    main()
