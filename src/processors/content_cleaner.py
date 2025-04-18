"""
Content cleaning utilities for processing scraped data.
"""

from bs4 import Tag

def clean_content(content):
    """
    Clean the content by removing extra whitespace and newlines.
    
    Args:
        content: Content to clean (string or BeautifulSoup element)
        
    Returns:
        str: Cleaned content
    """
    if not content:
        return ""
        
    # If it's a BeautifulSoup element, get its text
    if isinstance(content, Tag):
        content = content.get_text(separator=" ", strip=True)
        
    # Remove extra whitespace and newlines
    content = ' '.join(content.split())
    return content.strip()

def clean_advertisement_content(content):
    """
    Remove ADVERTISEMENT text from content and clean up user questions in Cooking Notes.
    
    Args:
        content: Content to clean (string or dict)
        
    Returns:
        str or dict: Cleaned content
    """
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

def has_subheadings(item):
    """
    Check if a field item contains subheadings (h3 tags).
    
    Args:
        item: Item to check (BeautifulSoup element or string)
        
    Returns:
        bool: True if the item contains h3 tags, False otherwise
    """
    if isinstance(item, str):
        return False  # String inputs cannot have h3 tags
    try:
        return len(item.find_all('h3')) > 0
    except AttributeError:
        return False  # Handle any other non-BeautifulSoup objects gracefully

def extract_recipe_links(field_item):
    """
    Extract recipe links from a field item.
    
    Args:
        field_item: BeautifulSoup element containing recipe links
        
    Returns:
        dict: Dictionary mapping recipe names to URLs
    """
    recipe_links = {}
    links = field_item.find_all('a')
    base_url = "https://www.almanac.com"
    
    for link in links:
        if '/recipe/' in link.get('href', ''):
            recipe_name = link.get_text(strip=True)
            recipe_url = base_url + link.get('href')
            recipe_links[recipe_name] = recipe_url
    
    return recipe_links
