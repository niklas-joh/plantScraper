"""
Tests for the HTTP utility module.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.http import get_soup, save_html_to_file, make_request_with_retry
from src import config

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.status_code = 200
    mock.content = b"<html><body><h1>Test Page</h1></body></html>"
    return mock

@pytest.fixture
def mock_failed_response():
    """Create a mock failed response object."""
    mock = MagicMock()
    mock.status_code = 404
    mock.content = b"Not Found"
    return mock

@patch("src.utils.http.requests.get")
def test_get_soup_success(mock_get, mock_response):
    """Test get_soup with a successful response."""
    mock_get.return_value = mock_response
    
    soup = get_soup("https://example.com")
    
    assert soup is not None
    assert soup.find("h1").text == "Test Page"
    mock_get.assert_called_once_with(
        "https://example.com",
        headers=config.HTTP_HEADERS,
        timeout=config.REQUEST_TIMEOUT,
        verify=config.VERIFY_SSL
    )

@patch("src.utils.http.requests.get")
def test_get_soup_failure(mock_get, mock_failed_response):
    """Test get_soup with a failed response."""
    mock_get.return_value = mock_failed_response
    
    soup = get_soup("https://example.com")
    
    assert soup is None
    mock_get.assert_called_once()

@patch("src.utils.http.requests.get")
def test_get_soup_exception(mock_get):
    """Test get_soup with an exception."""
    mock_get.side_effect = Exception("Connection error")
    
    soup = get_soup("https://example.com")
    
    assert soup is None
    mock_get.assert_called_once()

@patch("builtins.open", new_callable=MagicMock)
def test_save_html_to_file(mock_open):
    """Test save_html_to_file."""
    mock_content = MagicMock()
    mock_content.prettify.return_value = "<html>\n  <body>\n    <h1>Test Page</h1>\n  </body>\n</html>"
    
    save_html_to_file(mock_content, "test.html")
    
    mock_open.assert_called_once_with("test.html", "w", encoding="utf-8")
    mock_file = mock_open.return_value.__enter__.return_value
    mock_file.write.assert_called_once_with("<html>\n  <body>\n    <h1>Test Page</h1>\n  </body>\n</html>")

@patch("src.utils.http.requests.get")
@patch("src.utils.http.time.sleep")
def test_make_request_with_retry_success(mock_sleep, mock_get, mock_response):
    """Test make_request_with_retry with a successful response."""
    mock_get.return_value = mock_response
    
    response = make_request_with_retry("https://example.com")
    
    assert response is not None
    assert response.status_code == 200
    mock_get.assert_called_once()
    mock_sleep.assert_not_called()

@patch("src.utils.http.requests.get")
@patch("src.utils.http.time.sleep")
def test_make_request_with_retry_failure(mock_sleep, mock_get):
    """Test make_request_with_retry with failures."""
    mock_get.side_effect = [Exception("Connection error"), Exception("Connection error"), mock_response]
    
    response = make_request_with_retry("https://example.com", max_retries=3)
    
    assert response is None
    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2
