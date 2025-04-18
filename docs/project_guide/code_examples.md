# Plant Scraper Code Examples

This document provides practical code examples for working with the Plant Scraper project.

## Scraper Examples

### Running the Plant List Scraper

```python
from src.scraper.plant_list import PlantListScraper

# Initialize the scraper
scraper = PlantListScraper()

# Scrape plant list
plants = scraper.scrape()

# Save to CSV
if plants:
    scraper.save_to_csv(plants, "data/plants.csv")
```

### Running the Plant Details Scraper

```python
from src.scraper.plant_details import PlantDetailsScraper

# Initialize the scraper
scraper = PlantDetailsScraper(plants_csv="data/plants.csv")

# Scrape details for all plants (or limit to a specific number)
plants = scraper.scrape_all(limit=10)

# The scraper automatically saves progress to the output file
```

### Scraping a Single Plant

```python
from src.scraper.plant_details import PlantDetailsScraper

# Initialize the scraper
scraper = PlantDetailsScraper()

# Example plant row (would come from CSV in practice)
plant_row = {
    "Name": "Tomatoes",
    "Link": "https://www.almanac.com/plant/tomatoes",
    "Image URL": "https://www.almanac.com/sites/default/files/image_url.jpg"
}

# Scrape details for a single plant
plant_data = scraper.scrape_plant(plant_row, 0, 1)
```

## Content Cleaning Examples

### Cleaning Advertisement Content

```python
from src.processors.content_cleaner import clean_advertisement_content

# Example content with advertisement
content = "Growing tomatoes is easy. ADVERTISEMENT Learn more about soil requirements."

# Clean the content
cleaned_content = clean_advertisement_content(content)
print(cleaned_content)  # "Growing tomatoes is easy. Learn more about soil requirements."
```

### Filtering User Comments from Cooking Notes

```python
from src.processors.content_cleaner import filter_user_comments_from_cooking_notes

# Example cooking notes with user comments
cooking_notes = """
Bell peppers are delicious when roasted.

I tried growing bell peppers last year but they didn't do well. Any tips?

Bell peppers can be stuffed with rice and meat for a complete meal.
"""

# Filter out user comments
filtered_notes = filter_user_comments_from_cooking_notes(cooking_notes, "Bell peppers")
print(filtered_notes)  # Only contains cooking instructions, not user questions
```

### Extracting Recipe Links

```python
from bs4 import BeautifulSoup
from src.processors.content_cleaner import extract_recipe_links

# Example HTML with recipe links
html = """
<div>
  <p>Try these delicious recipes:</p>
  <ul>
    <li><a href="/recipe/stuffed-peppers">Stuffed Peppers</a></li>
    <li><a href="/recipe/roasted-peppers">Roasted Peppers</a></li>
  </ul>
</div>
"""

# Parse HTML
soup = BeautifulSoup(html, "html.parser")

# Extract recipe links
recipe_links = extract_recipe_links(soup)
print(recipe_links)
# {
#   "Stuffed Peppers": "https://www.almanac.com/recipe/stuffed-peppers",
#   "Roasted Peppers": "https://www.almanac.com/recipe/roasted-peppers"
# }
```

## Notion Integration Examples

### Transforming Plant Data to Notion Format

```python
from scripts.sync_to_notion_requests import transform_plant_to_notion_properties

# Example plant data
plant = {
    "Name": "Tomatoes",
    "Botanical Name": "Solanum lycopersicum",
    "Plant Type": "Annual",
    "Sun Exposure": "Full Sun",
    "Soil pH": "Acidic to Neutral",
    "Bloom Time": "Summer",
    "Flower Color": "Yellow",
    "Hardiness Zone": "3-9",
    "Link": "https://www.almanac.com/plant/tomatoes",
    "Image URL": "https://www.almanac.com/sites/default/files/image_url.jpg",
    "Planting": "Plant tomatoes in spring after all danger of frost has passed.",
    "Growing": "Water regularly and provide support for growing plants.",
    "Harvesting": "Harvest when fruits are firm and fully colored."
}

# Transform to Notion properties
notion_properties = transform_plant_to_notion_properties(plant)
```

### Creating Notion Content Blocks

```python
from scripts.sync_to_notion_requests import create_plant_content_blocks

# Example plant data (same as above)
plant = {
    "Name": "Tomatoes",
    # ... other fields ...
    "Pests/Diseases": {
        "headers": ["Pest/Disease", "Type", "Symptoms", "Control"],
        "rows": [
            {
                "pest": "Aphids",
                "type": "Insect",
                "symptoms": "Curled leaves, stunted growth",
                "control": "Insecticidal soap, neem oil"
            }
        ]
    },
    "Recipes": {
        "Tomato Sauce": "https://www.almanac.com/recipe/tomato-sauce",
        "Fried Green Tomatoes": "https://www.almanac.com/recipe/fried-green-tomatoes"
    }
}

# Create content blocks
content_blocks = create_plant_content_blocks(plant)
```

### Syncing a Plant to Notion

```python
import os
from scripts.sync_to_notion_requests import sync_plant_to_notion, get_existing_plants

# Get API key and database ID from environment variables
api_key = os.getenv("NOTION_API_KEY")
database_id = os.getenv("NOTION_DATABASE_ID")

# Example plant data
plant = {
    "Name": "Tomatoes",
    # ... other fields ...
}

# Get existing plants in the database
existing_plants = get_existing_plants(api_key, database_id)

# Sync the plant to Notion
success, action, error_message = sync_plant_to_notion(api_key, database_id, plant, existing_plants)

if success:
    print(f"Plant {action} successfully")
else:
    print(f"Error: {error_message}")
```

## GitHub Integration Examples

### Creating a GitHub Issue

```python
from src.github.create_issues import create_issue

# Example issue data
issue = {
    "title": "Fix Bell Peppers Wit and Wisdom field",
    "body": "The Wit and Wisdom field for Bell Peppers is stored as a dictionary, but Notion expects a string.",
    "labels": ["bug", "notion-integration"]
}

# Create the issue
issue_number = create_issue(issue)
print(f"Created issue #{issue_number}")
```

### Commenting on a GitHub Issue

```python
from src.github.issue_manager import comment_on_issue

# Comment on an issue
comment_on_issue(
    issue_number=5,
    comment="I've fixed this issue by modifying the sync_to_notion_requests.py script to handle both string and dictionary formats.",
    owner="niklas-joh",
    repo="plantScraper"
)
```

## File I/O Examples

### Loading Plants Data

```python
import json
from src.utils.file_io import load_from_csv, load_from_json

# Load basic plant data from CSV
plants_df = load_from_csv("data/plants.csv")

# Load detailed plant data from JSON
with open("output/plants_detailed.json", "r", encoding="utf-8") as f:
    plants_detailed = json.load(f)
```

### Saving Plants Data

```python
import json
from src.utils.file_io import save_to_csv, save_to_json

# Save basic plant data to CSV
save_to_csv(plants_df, "data/plants.csv")

# Save detailed plant data to JSON
save_to_json(plants_detailed, "output/plants_detailed.json")
```

## Handling the Bell Peppers Issue

### Converting Dictionary to String

```python
# Example Bell Peppers Wit and Wisdom field as a dictionary
wit_wisdom = {
    "content": "Sweet bell peppers do not contain capsaicin...",
    "sub_headings": {
        "Do different-colored peppers come from different plants?": "Surprisingly enough, the green and red bell peppers...",
        "Are there male and female peppers?": "There is a popular myth that states that pepper fruits..."
    }
}

# Convert to string
formatted_content = wit_wisdom["content"]

# Add sub-headings to the content
for sub_heading, sub_content in wit_wisdom["sub_headings"].items():
    formatted_content += f"\n\n{sub_heading}\n{sub_content}"

# Now formatted_content is a string that can be sent to Notion
```

### Handling Both String and Dictionary Formats

```python
# Function to handle both formats
def process_wit_wisdom(wit_wisdom):
    if isinstance(wit_wisdom, dict):
        content = wit_wisdom.get("content", "")
        sub_headings = wit_wisdom.get("sub_headings", {})
        
        formatted_content = content
        
        # Add sub-headings to the content
        for sub_heading, sub_content in sub_headings.items():
            formatted_content += f"\n\n{sub_heading}\n{sub_content}"
            
        return formatted_content
    else:
        # Already a string
        return wit_wisdom

# Example usage
plant = {
    "Name": "Bell Peppers",
    "Wit and Wisdom": {
        "content": "Sweet bell peppers do not contain capsaicin...",
        "sub_headings": {
            "Do different-colored peppers come from different plants?": "Surprisingly enough, the green and red bell peppers..."
        }
    }
}

# Process the Wit and Wisdom field
plant["Wit and Wisdom"] = process_wit_wisdom(plant["Wit and Wisdom"])
