# Plant Scraper Troubleshooting Guide

This guide addresses common issues you might encounter when working with the Plant Scraper project and provides solutions to resolve them.

## Scraper Issues

### Issue: Scraper fails to retrieve plant data

**Symptoms:**
- Empty results from `PlantListScraper` or `PlantDetailsScraper`
- HTTP connection errors

**Possible Causes:**
1. Network connectivity issues
2. Website structure has changed
3. Rate limiting or IP blocking by the website

**Solutions:**

1. **Check your internet connection**
   ```bash
   ping www.almanac.com
   ```

2. **Adjust request delay to avoid rate limiting**
   ```python
   # Increase delay between requests
   scraper = PlantDetailsScraper(delay=3)  # 3 seconds between requests
   ```

3. **Update user agent in config.py**
   ```python
   # In src/config.py
   HTTP_HEADERS = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
   }
   ```

4. **Check if website structure has changed**
   - Manually visit the website and inspect the HTML structure
   - Update the scraper code if selectors have changed

### Issue: Scraper extracts incomplete or incorrect data

**Symptoms:**
- Missing fields in scraped data
- Malformed content in certain fields

**Solutions:**

1. **Debug the scraper with a single plant**
   ```python
   from src.scraper.plant_details import PlantDetailsScraper
   
   # Initialize the scraper
   scraper = PlantDetailsScraper()
   
   # Example plant row
   plant_row = {
       "Name": "Tomatoes",
       "Link": "https://www.almanac.com/plant/tomatoes",
       "Image URL": "https://www.almanac.com/sites/default/files/image_url.jpg"
   }
   
   # Enable verbose output
   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Scrape details for a single plant
   plant_data = scraper.scrape_plant(plant_row, 0, 1)
   
   # Examine the result
   import json
   print(json.dumps(plant_data, indent=2))
   ```

2. **Update content extraction logic if needed**
   - Check `extract_content_between_elements` function in `src/scraper/base.py`
   - Update selectors or extraction logic based on website changes

## Notion Integration Issues

### Issue: "Wit and Wisdom" field format error

**Symptoms:**
- Error when syncing to Notion: `body.properties.Wit and Wisdom.rich_text[0].text.content should be a string`
- Sync fails specifically for Bell Peppers or other plants

**Solutions:**

1. **Fix the specific plant in the JSON file**
   ```python
   import json
   import os
   
   # Load the plants data
   plants_file = os.path.join("output", "plants_detailed.json")
   with open(plants_file, 'r', encoding='utf-8') as f:
       plants = json.load(f)
   
   # Find Bell Peppers and fix the Wit and Wisdom field
   for plant in plants:
       if plant.get("Name") == "Bell Peppers":
           wit_wisdom = plant.get("Wit and Wisdom")
           
           if isinstance(wit_wisdom, dict):
               # Convert the dictionary to a string
               content = wit_wisdom.get("content", "")
               sub_headings = wit_wisdom.get("sub_headings", {})
               
               formatted_content = content
               
               # Add sub-headings to the content
               for sub_heading, sub_content in sub_headings.items():
                   formatted_content += f"\n\n{sub_heading}\n{sub_content}"
               
               # Replace the dictionary with the formatted string
               plant["Wit and Wisdom"] = formatted_content
               print("Fixed 'Wit and Wisdom' field for Bell Peppers")
   
   # Save the updated plants data
   with open(plants_file, 'w', encoding='utf-8') as f:
       json.dump(plants, f, indent=2)
   ```

2. **Update the sync script to handle both formats**
   ```python
   # In scripts/sync_to_notion_requests.py
   
   # Modify the transform_plant_to_notion_properties function
   def transform_plant_to_notion_properties(plant):
       # ... existing code ...
       
       # Add Wit and Wisdom if available
       if "Wit and Wisdom" in plant:
           content = ""
           wit_wisdom = plant["Wit and Wisdom"]
           
           # Handle both string and dictionary formats
           if isinstance(wit_wisdom, dict):
               if "content" in wit_wisdom:
                   content = wit_wisdom["content"]
                   
                   # Add sub-headings if they exist
                   if "sub_headings" in wit_wisdom:
                       for sub_heading, sub_content in wit_wisdom["sub_headings"].items():
                           content += f"\n\n{sub_heading}\n{sub_content}"
           else:
               content = wit_wisdom
               
           if content:
               # Truncate content if it's too long for a property
               max_length = 2000
               if len(content) > max_length:
                   content = content[:max_length-3] + "..."
                   
               properties["Wit and Wisdom"] = {
                   "rich_text": [
                       {
                           "text": {
                               "content": content
                           }
                       }
                   ]
               }
       
       # ... rest of the function ...
   ```

### Issue: Notion API rate limiting

**Symptoms:**
- HTTP 429 "Too Many Requests" errors
- Sync fails after processing several plants

**Solutions:**

1. **Increase delay between requests**
   ```python
   # In scripts/sync_to_notion_requests.py, modify the time.sleep() call
   time.sleep(1.0)  # Increase from 0.5 to 1.0 seconds
   ```

2. **Sync in smaller batches**
   ```bash
   # Sync first 10 plants
   python scripts/sync_to_notion_requests.py --limit 10
   
   # Sync next 10 plants
   python scripts/sync_to_notion_requests.py --limit 10 --offset 10
   
   # Continue with additional batches
   python scripts/sync_to_notion_requests.py --limit 10 --offset 20
   ```

### Issue: Content too long for Notion

**Symptoms:**
- Error about content exceeding Notion's limits
- Truncated content in Notion database

**Solution:**

The sync script already includes logic to truncate content that exceeds Notion's 2000 character limit. If you're still encountering issues:

1. **Check the truncation logic**
   ```python
   # Ensure this logic is applied to all text fields
   if len(content) > 2000:
       content = content[:1997] + "..."
   ```

2. **Split very long content into multiple blocks**
   ```python
   # For very long content, split into multiple paragraph blocks
   if len(content) > 2000:
       chunks = [content[i:i+1997] for i in range(0, len(content), 1997)]
       for chunk in chunks:
           blocks.append({
               "object": "block",
               "type": "paragraph",
               "paragraph": {
                   "rich_text": [
                       {
                           "type": "text",
                           "text": {
                               "content": chunk
                           }
                       }
                   ]
               }
           })
   else:
       # Original block creation code for shorter content
   ```

## GitHub Integration Issues

### Issue: GitHub authentication fails

**Symptoms:**
- "Authentication failed" errors when using GitHub integration
- Permission denied errors

**Solutions:**

1. **Check GitHub CLI authentication**
   ```bash
   gh auth status
   ```

2. **Re-authenticate if needed**
   ```bash
   gh auth login
   ```

3. **Verify environment variables**
   ```bash
   echo $GITHUB_OWNER
   echo $GITHUB_REPO
   ```

4. **Update environment variables in .env file**
   ```
   GITHUB_OWNER=your-github-username
   GITHUB_REPO=plantScraper
   ```

## Data Processing Issues

### Issue: User comments not properly filtered from Cooking Notes

**Symptoms:**
- Cooking Notes field contains user questions or comments
- Non-cooking related content in Cooking Notes

**Solution:**

1. **Update the filtering patterns in content_cleaner.py**
   ```python
   # Add additional patterns to user_comment_indicators
   user_comment_indicators = [
       # Existing patterns...
       r'\bI\s+have\b', r'\bI\s+need\b', r'\bI\s+want\b',
       r'\bI\s+was\b', r'\bI\s+am\b', r'\bI\s+will\b',
       # Add more patterns as needed
   ]
   ```

2. **Test the filtering with specific content**
   ```python
   from src.processors.content_cleaner import filter_user_comments_from_cooking_notes
   
   # Example content with user comments
   content = """
   Bell peppers are delicious when roasted.
   
   I tried growing bell peppers last year but they didn't do well. Any tips?
   
   Bell peppers can be stuffed with rice and meat for a complete meal.
   """
   
   # Filter the content
   filtered = filter_user_comments_from_cooking_notes(content, "Bell peppers")
   print(filtered)
   ```

## Environment and Configuration Issues

### Issue: Missing environment variables

**Symptoms:**
- "Notion API key not provided" errors
- "Database ID not provided" errors

**Solutions:**

1. **Create or update .env file**
   ```bash
   # Create .env file if it doesn't exist
   touch .env
   
   # Edit the file
   nano .env
   ```
   
   Add the required variables:
   ```
   NOTION_API_KEY=your_notion_api_key
   NOTION_DATABASE_ID=your_notion_database_id
   GITHUB_OWNER=your_github_username
   GITHUB_REPO=plantScraper
   ```

2. **Load environment variables in your script**
   ```python
   from dotenv import load_dotenv
   from pathlib import Path
   
   # Load environment variables from .env file
   dotenv_path = Path(__file__).resolve().parent.parent / '.env'
   load_dotenv(dotenv_path)
   ```

### Issue: Output directories don't exist

**Symptoms:**
- "No such file or directory" errors
- File saving failures

**Solution:**

The config.py file should already create necessary directories:

```python
# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

If you're using custom directories, ensure they exist:

```python
import os

# Create custom directory
custom_dir = "custom_output"
os.makedirs(custom_dir, exist_ok=True)
```

## Debugging Tips

### Enable Verbose Logging

```python
import logging

# Set logging level to DEBUG for more detailed output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Inspect Network Requests

```python
# Add this to your script to see HTTP request details
import requests
from http.client import HTTPConnection
HTTPConnection.debuglevel = 1
```

### Save Intermediate Results

```python
# Save intermediate results for debugging
import json

def save_debug_data(data, filename):
    with open(f"debug/{filename}", 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Example usage
save_debug_data(plant_data, "debug_plant_data.json")
```

### Test Individual Components

```python
# Test content cleaner in isolation
from src.processors.content_cleaner import clean_advertisement_content

# Example content
content = "Growing tomatoes is easy. ADVERTISEMENT Learn more about soil requirements."

# Test cleaning
cleaned = clean_advertisement_content(content)
print(f"Original: {content}")
print(f"Cleaned: {cleaned}")
```

## Getting Help

If you encounter issues not covered in this guide:

1. Check the project documentation in the `docs/` directory
2. Look for similar issues in the GitHub repository
3. Create a new GitHub issue with:
   - Detailed description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Environment information (Python version, OS, etc.)
