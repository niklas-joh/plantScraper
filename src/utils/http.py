"""
HTTP utility functions for making requests and handling responses.
"""

import requests
import time
from bs4 import BeautifulSoup
import urllib3
from src import config

# Disable SSL verification warnings if configured
if not config.VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_soup(url, headers=None, timeout=None, verify=None):
    """
    Get BeautifulSoup object from URL.
    
    Args:
        url (str): URL to request
        headers (dict, optional): HTTP headers to use. Defaults to config.HTTP_HEADERS.
        timeout (int, optional): Request timeout in seconds. Defaults to config.REQUEST_TIMEOUT.
        verify (bool, optional): Whether to verify SSL certificates. Defaults to config.VERIFY_SSL.
        
    Returns:
        BeautifulSoup: Parsed HTML content or None if request failed
    """
    headers = headers or config.HTTP_HEADERS
    timeout = timeout or config.REQUEST_TIMEOUT
    verify = config.VERIFY_SSL if verify is None else verify
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
        if response.status_code != 200:
            print(f"  ⚠️ Request failed with status {response.status_code}")
            return None
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Request error: {str(e)}")
        return None

def save_html_to_file(content, filename):
    """
    Save HTML content to a file.
    
    Args:
        content (BeautifulSoup): BeautifulSoup object to save
        filename (str): Path to save the file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content.prettify())
    print(f"Content saved to {filename}")

def make_request_with_retry(url, headers=None, timeout=None, verify=None, max_retries=3, retry_delay=2):
    """
    Make a request with retry logic.
    
    Args:
        url (str): URL to request
        headers (dict, optional): HTTP headers to use. Defaults to config.HTTP_HEADERS.
        timeout (int, optional): Request timeout in seconds. Defaults to config.REQUEST_TIMEOUT.
        verify (bool, optional): Whether to verify SSL certificates. Defaults to config.VERIFY_SSL.
        max_retries (int, optional): Maximum number of retries. Defaults to 3.
        retry_delay (int, optional): Delay between retries in seconds. Defaults to 2.
        
    Returns:
        requests.Response: Response object or None if all retries failed
    """
    headers = headers or config.HTTP_HEADERS
    timeout = timeout or config.REQUEST_TIMEOUT
    verify = config.VERIFY_SSL if verify is None else verify
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout, verify=verify)
            return response
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️ Request failed (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"  ❌ All retries failed")
                return None
