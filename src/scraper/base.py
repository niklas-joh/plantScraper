"""
Base scraper functionality for all scrapers.
"""

import time
from bs4 import Tag
from src.utils.http import get_soup
from src.processors.content_cleaner import clean_content, clean_advertisement_content
from src import config

def extract_content_between_elements(start_elem, end_elem=None, stop_text=None, special_handling=None):
    """
    Extract content between two elements or until a specific text is found.
    
    Args:
        start_elem: The starting element
        end_elem: The ending element (optional)
        stop_text: Text to stop extraction at (optional)
        special_handling: Function to handle special elements (optional)
    
    Returns:
        Extracted content as string or structured data for tables
    """
    if not start_elem:
        return ""
        
    content = []
    structured_data = None  # For storing table data
    current_elem = start_elem.next_sibling
    
    while current_elem and (end_elem is None or current_elem != end_elem):
        if isinstance(current_elem, Tag):
            if current_elem.name != 'h3':  # Skip any nested h3
                if special_handling:
                    # Special handling returned content, use it
                    special_content, should_stop = special_handling(current_elem, "".join(content) if content else "")
                    
                    # If we got structured data (like a table), store it separately
                    if special_content and isinstance(special_content, dict) and "headers" in special_content and "rows" in special_content:
                        structured_data = special_content
                        should_stop = True  # Stop after finding a table
                    elif special_content:
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
    
    # Return structured data if we found a table, otherwise join content as string
    if structured_data:
        return structured_data
    else:
        return " ".join(content).strip()

def process_table(table_tag):
    """
    Process a table tag and return a structured format with headers and rows.
    For Pests/Diseases tables, uses specific keys in the expected format.
    
    Args:
        table_tag: BeautifulSoup table element
        
    Returns:
        dict: Dictionary with headers and rows
    """
    # Check if this is a pests/diseases table by looking for the caption or headers
    is_pest_table = False
    caption = table_tag.find('caption')
    if caption and "Pests and Diseases" in caption.get_text():
        is_pest_table = True
    
    # Also check headers for "Pest/Disease" column
    if table_tag.find(string=lambda text: text and "Pest/Disease" in text):
        is_pest_table = True
    
    if is_pest_table:
        # This is a pests/diseases table
        # First, extract the column headers from the thead section
        thead = table_tag.find('thead')
        if thead:
            headers_row = thead.find('tr')
            headers = [header.get_text(strip=True) for header in headers_row.find_all('th')]
        else:
            # If no thead, try to get headers from the first row
            headers_row = table_tag.find('tr')
            if not headers_row:
                return {"headers": [], "rows": []}
            headers = [header.get_text(strip=True) for header in headers_row.find_all('th')]
        
        # Process data rows from the tbody section
        tbody = table_tag.find('tbody')
        if tbody:
            data_rows = tbody.find_all('tr')
        else:
            # If no tbody, use all rows except the first (header) row
            data_rows = table_tag.find_all('tr')[1:]
        
        processed_rows = []
        
        for row in data_rows:
            # In this table, the pest name is in a th tag, not a td tag
            pest_cell = row.find('th')
            if not pest_cell:
                continue
                
            # Get all td cells for the other columns
            cells = row.find_all('td')
            if len(cells) < 3:  # Need at least type, symptoms, and control
                continue
                
            # Create row data with standardized keys
            row_data = {
                "pest": pest_cell.get_text(strip=True),
                "type": cells[0].get_text(strip=True),
                "symptoms": cells[1].get_text(strip=True),
                "control": cells[2].get_text(strip=True)
            }
            
            processed_rows.append(row_data)
        
        # Return structured format with headers and rows
        return {
            "headers": headers,
            "rows": processed_rows
        }
    else:
        # Generic table processing for non-pest tables
        headers = [header.get_text(strip=True) for header in table_tag.find_all('th')]
        
        # Skip the header row when processing rows
        rows = table_tag.find_all('tr')[1:] if headers else table_tag.find_all('tr')
        
        # Process rows
        processed_rows = []
        for row in rows:
            cells = row.find_all('td')
            # Skip rows without enough cells
            if len(cells) < len(headers):
                continue
                
            row_data = {}
            for i, cell in enumerate(cells):
                if i < len(headers):  # Ensure we don't exceed headers length
                    row_data[headers[i]] = cell.get_text(strip=True)
            processed_rows.append(row_data)
        
        # Return structured format with headers and rows
        return {
            "headers": headers,
            "rows": processed_rows
        }

def handle_special_elements(elem, content):
    """
    Handle special elements like tables.
    
    Args:
        elem: BeautifulSoup element to handle
        content: Current content string
        
    Returns:
        tuple: (processed_content, should_stop)
    """
    if elem.name == 'table':
        # Return the table data structure directly
        # The False indicates we don't want to stop processing
        return process_table(elem), False
    return None, False

class BaseScraper:
    """Base class for all scrapers."""
    
    def __init__(self, headers=None, timeout=None, verify=None, delay=None):
        """
        Initialize the scraper.
        
        Args:
            headers (dict, optional): HTTP headers to use. Defaults to config.HTTP_HEADERS.
            timeout (int, optional): Request timeout in seconds. Defaults to config.REQUEST_TIMEOUT.
            verify (bool, optional): Whether to verify SSL certificates. Defaults to config.VERIFY_SSL.
            delay (int, optional): Delay between requests in seconds. Defaults to config.REQUEST_DELAY.
        """
        self.headers = headers or config.HTTP_HEADERS
        self.timeout = timeout or config.REQUEST_TIMEOUT
        self.verify = config.VERIFY_SSL if verify is None else verify
        self.delay = delay or config.REQUEST_DELAY
    
    def get_soup(self, url):
        """
        Get BeautifulSoup object from URL.
        
        Args:
            url (str): URL to request
            
        Returns:
            BeautifulSoup: Parsed HTML content or None if request failed
        """
        return get_soup(url, self.headers, self.timeout, self.verify)
    
    def scrape(self, url):
        """
        Scrape a URL.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            dict: Scraped data or None if scraping failed
        """
        raise NotImplementedError("Subclasses must implement scrape()")
    
    def process_data(self, data):
        """
        Process scraped data.
        
        Args:
            data: Data to process
            
        Returns:
            dict: Processed data
        """
        raise NotImplementedError("Subclasses must implement process_data()")
    
    def sleep(self):
        """Sleep between requests to be polite to the server."""
        time.sleep(self.delay)
