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
                        plant_data[current_label] = ""
                    elif 'field__item' in child.get('class', []) and current_label:
                        content = child.get_text(separator=" ", strip=True)
                        if plant_data[current_label]:
                            plant_data[current_label] += f"\n{content}"
                        else:
                            plant_data[current_label] = f"{content}"

        # Save plant data
        all_plants.append(plant_data)
        # print(json.dumps(plant_data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"  ❌ Error: {e}")

    time.sleep(0.5)  # Be polite to their servers

# Save to JSON
with open("plants_detailed.json", "w", encoding="utf-8") as f:
    json.dump(all_plants, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done. Saved {len(all_plants)} plants to plants_detailed.json")