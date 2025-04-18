"""
Content cleaning utilities for processing scraped data.
"""

import re
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

def filter_user_comments_from_cooking_notes(content, plant_name=None):
    """
    Filter out user comments from Cooking Notes content.
    
    Args:
        content (str): Cooking Notes content
        plant_name (str, optional): Name of the plant. If provided, will prioritize content
                                   that mentions the plant name. Defaults to None.
        
    Returns:
        str: Filtered content with only cooking instructions
    """
    if not content:
        return ""
    
    # Extract plant name from content if not provided
    if not plant_name:
        # Try to extract from first line or paragraph
        first_paragraph = content.split('\n')[0]
        words = first_paragraph.split()
        if words:
            # Assume the first word might be the plant name
            plant_name = words[0].lower()
    
    # Split content into paragraphs
    paragraphs = content.split('\n')
    
    # First pass: identify cooking instructions that mention the plant
    cooking_instructions = []
    
    # Patterns that strongly indicate cooking instructions
    cooking_indicators = [
        r'\bcook\w*\b', r'\bprep\w*\b', r'\brecipe\w*\b', r'\beat\w*\b', r'\bfood\b',
        r'\bdelicious\b', r'\btasty\b', r'\bflavor\w*\b', r'\bserve\w*\b', r'\bdish\w*\b',
        r'\bmeal\w*\b', r'\bingredient\w*\b', r'\bboil\w*\b', r'\broast\w*\b', r'\bbake\w*\b',
        r'\bsteam\w*\b', r'\bgrill\w*\b', r'\bfry\w*\b', r'\bsauté\w*\b', r'\bsaute\w*\b',
        r'\bsimmer\w*\b', r'\bbroil\w*\b', r'\bheat\w*\b', r'\bwarm\w*\b', r'\bmicrowave\w*\b',
        r'\btoast\w*\b', r'\bstir\w*\b', r'\bmix\w*\b', r'\bblend\w*\b', r'\bwhisk\w*\b',
        r'\bchop\w*\b', r'\bdice\w*\b', r'\bslice\w*\b', r'\bmince\w*\b', r'\bgrate\w*\b',
        r'\bpeel\w*\b', r'\bcut\w*\b', r'\btrim\w*\b', r'\bwash\w*\b', r'\brinse\w*\b',
        r'\bdrain\w*\b', r'\bsoak\w*\b', r'\bmarinate\w*\b', r'\bseason\w*\b', r'\bsprinkle\w*\b',
        r'\bdrizzle\w*\b', r'\bpour\w*\b', r'\bmeasure\w*\b', r'\bweigh\w*\b'
    ]
    
    # Patterns that strongly indicate user comments/questions
    user_comment_indicators = [
        r'\?\s*$',  # Ends with question mark
        r'^\s*Hi\s', r'^\s*Hello\s', r'^\s*Thanks\s', r'^\s*Thank you\s',
        r'^\s*Why\s', r'^\s*How\s', r'^\s*What\s', r'^\s*Where\s', r'^\s*When\s',
        r'^\s*Who\s', r'^\s*Can\s', r'^\s*Do\s', r'^\s*Does\s', r'^\s*Is\s',
        r'^\s*Are\s', r'^\s*Will\s', r'^\s*Should\s', r'^\s*Could\s', r'^\s*Would\s',
        r'\bI\s', r'\bI\'', r'\bI\'ve\b', r'\bI\'m\b', r'\bI\'d\b', r'\bI\'ll\b',
        r'\bmy\b', r'\bmine\b', r'\bwe\b', r'\bwe\'', r'\bwe\'ve\b', r'\bwe\'re\b',
        r'\bwe\'d\b', r'\bwe\'ll\b', r'\bour\b', r'\bours\b'
    ]
    
    # Topics that are clearly not cooking-related
    non_cooking_topics = [
        r'\bpest\w*\b', r'\bdisease\w*\b', r'\binsect\w*\b', r'\bbeetle\w*\b', r'\bbug\w*\b',
        r'\bgrub\w*\b', r'\bfertiliz\w*\b', r'\bsoil\b', r'\bplant\w*\b', r'\bgrow\w*\b',
        r'\bgarden\w*\b', r'\byard\b', r'\blawn\b', r'\bseed\w*\b', r'\bsprout\w*\b',
        r'\broot\w*\b', r'\bleaf\b', r'\bleaves\b', r'\bstem\w*\b', r'\bflower\w*\b',
        r'\bbloom\w*\b', r'\bwater\w*\b', r'\birrigat\w*\b', r'\bsunlight\b', r'\bshade\b',
        r'\btemperature\b', r'\bweather\b', r'\bseason\w*\b', r'\bspring\b', r'\bsummer\b',
        r'\bfall\b', r'\bautumn\b', r'\bwinter\b', r'\bharvest\w*\b', r'\bduck\b', r'\bpet\b'
    ]
    
    # Nutrition and health terms that are relevant to cooking
    nutrition_terms = [
        r'\bnutrient\w*\b', r'\bvitamin\w*\b', r'\bmineral\w*\b', r'\bprotein\b', 
        r'\bfiber\b', r'\bhealth\w*\b', r'\bnutrition\w*\b', r'\bbeneficial\b', 
        r'\bsuperfood\b', r'\bantioxidant\w*\b', r'\banti-inflammatory\b'
    ]
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Skip paragraphs that contain non-cooking topics
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in non_cooking_topics):
            # But keep if it specifically mentions cooking the plant
            if plant_name and any(re.search(fr'\b{pattern}\b', paragraph, re.IGNORECASE) for pattern in [
                f'cook {plant_name}', f'cooking {plant_name}', f'prepare {plant_name}', 
                f'eat {plant_name}', f'{plant_name} recipe', f'{plant_name} dish'
            ]):
                cooking_instructions.append(paragraph)
            continue
            
        # Skip paragraphs that are clearly user comments
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in user_comment_indicators):
            # But keep if it specifically mentions cooking the plant
            if plant_name and any(re.search(fr'\b{pattern}\b', paragraph, re.IGNORECASE) for pattern in [
                f'cook {plant_name}', f'cooking {plant_name}', f'prepare {plant_name}', 
                f'eat {plant_name}', f'{plant_name} recipe', f'{plant_name} dish'
            ]):
                cooking_instructions.append(paragraph)
            continue
        
        # Keep paragraphs with strong cooking indicators
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in cooking_indicators):
            cooking_instructions.append(paragraph)
            continue
            
        # Keep paragraphs that are clearly about nutrition
        if any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in nutrition_terms):
            cooking_instructions.append(paragraph)
    
    # Join filtered paragraphs back into a string
    filtered_content = '\n'.join(cooking_instructions)
    
    # If we filtered out everything, return a message
    if not filtered_content.strip():
        return "No cooking instructions available."
    
    return filtered_content

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
    if "Cooking Notes" in content or "nutrient-dense" in content:  # Indicators for Cooking Notes
        # Filter out user comments from Cooking Notes
        return filter_user_comments_from_cooking_notes(content)
        
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
