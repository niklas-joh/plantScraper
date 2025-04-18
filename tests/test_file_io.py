"""
Tests for the file I/O utility module.
"""

import os
import sys
import json
import pytest
import pandas as pd
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.file_io import (
    ensure_directory_exists,
    save_to_csv,
    save_to_json,
    load_from_csv,
    load_from_json
)
from src import config

@patch("os.makedirs")
def test_ensure_directory_exists(mock_makedirs):
    """Test ensure_directory_exists."""
    ensure_directory_exists("test_dir")
    mock_makedirs.assert_called_once_with("test_dir", exist_ok=True)

@patch("os.path.dirname")
@patch("src.utils.file_io.ensure_directory_exists")
@patch("pandas.DataFrame.to_csv")
def test_save_to_csv_list(mock_to_csv, mock_ensure_dir, mock_dirname):
    """Test save_to_csv with a list."""
    mock_dirname.return_value = "test_dir"
    
    data = [{"name": "Plant 1", "url": "http://example.com/1"}]
    result = save_to_csv(data, "test.csv")
    
    assert result is True
    mock_dirname.assert_called_once_with("test.csv")
    mock_ensure_dir.assert_called_once_with("test_dir")
    mock_to_csv.assert_called_once_with("test.csv", index=False)

@patch("os.path.dirname")
@patch("src.utils.file_io.ensure_directory_exists")
@patch("pandas.DataFrame.to_csv")
def test_save_to_csv_dataframe(mock_to_csv, mock_ensure_dir, mock_dirname):
    """Test save_to_csv with a DataFrame."""
    mock_dirname.return_value = "test_dir"
    
    data = pd.DataFrame([{"name": "Plant 1", "url": "http://example.com/1"}])
    result = save_to_csv(data, "test.csv")
    
    assert result is True
    mock_dirname.assert_called_once_with("test.csv")
    mock_ensure_dir.assert_called_once_with("test_dir")
    mock_to_csv.assert_called_once_with("test.csv", index=False)

@patch("os.path.dirname")
@patch("src.utils.file_io.ensure_directory_exists")
@patch("pandas.DataFrame.to_csv")
def test_save_to_csv_exception(mock_to_csv, mock_ensure_dir, mock_dirname):
    """Test save_to_csv with an exception."""
    mock_dirname.return_value = "test_dir"
    mock_to_csv.side_effect = Exception("CSV error")
    
    data = [{"name": "Plant 1", "url": "http://example.com/1"}]
    result = save_to_csv(data, "test.csv")
    
    assert result is False
    mock_dirname.assert_called_once_with("test.csv")
    mock_ensure_dir.assert_called_once_with("test_dir")
    mock_to_csv.assert_called_once()

@patch("os.path.dirname")
@patch("src.utils.file_io.ensure_directory_exists")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_to_json(mock_json_dump, mock_file, mock_ensure_dir, mock_dirname):
    """Test save_to_json."""
    mock_dirname.return_value = "test_dir"
    
    data = {"name": "Plant 1", "url": "http://example.com/1"}
    result = save_to_json(data, "test.json")
    
    assert result is True
    mock_dirname.assert_called_once_with("test.json")
    mock_ensure_dir.assert_called_once_with("test_dir")
    mock_file.assert_called_once_with("test.json", "w", encoding="utf-8")
    mock_json_dump.assert_called_once_with(data, mock_file(), indent=2, ensure_ascii=False)

@patch("os.path.dirname")
@patch("src.utils.file_io.ensure_directory_exists")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_to_json_exception(mock_json_dump, mock_file, mock_ensure_dir, mock_dirname):
    """Test save_to_json with an exception."""
    mock_dirname.return_value = "test_dir"
    mock_json_dump.side_effect = Exception("JSON error")
    
    data = {"name": "Plant 1", "url": "http://example.com/1"}
    result = save_to_json(data, "test.json")
    
    assert result is False
    mock_dirname.assert_called_once_with("test.json")
    mock_ensure_dir.assert_called_once_with("test_dir")
    mock_file.assert_called_once_with("test.json", "w", encoding="utf-8")
    mock_json_dump.assert_called_once()

@patch("pandas.read_csv")
def test_load_from_csv(mock_read_csv):
    """Test load_from_csv."""
    mock_df = pd.DataFrame([{"name": "Plant 1", "url": "http://example.com/1"}])
    mock_read_csv.return_value = mock_df
    
    result = load_from_csv("test.csv")
    
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    mock_read_csv.assert_called_once_with("test.csv")

@patch("pandas.read_csv")
def test_load_from_csv_exception(mock_read_csv):
    """Test load_from_csv with an exception."""
    mock_read_csv.side_effect = Exception("CSV error")
    
    result = load_from_csv("test.csv")
    
    assert result is None
    mock_read_csv.assert_called_once_with("test.csv")

@patch("builtins.open", new_callable=mock_open, read_data='{"name": "Plant 1", "url": "http://example.com/1"}')
@patch("json.load")
def test_load_from_json(mock_json_load, mock_file):
    """Test load_from_json."""
    mock_data = {"name": "Plant 1", "url": "http://example.com/1"}
    mock_json_load.return_value = mock_data
    
    result = load_from_json("test.json")
    
    assert result is not None
    assert result == mock_data
    mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")
    mock_json_load.assert_called_once_with(mock_file())

@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
def test_load_from_json_exception(mock_json_load, mock_file):
    """Test load_from_json with an exception."""
    mock_json_load.side_effect = Exception("JSON error")
    
    result = load_from_json("test.json")
    
    assert result is None
    mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")
    mock_json_load.assert_called_once()
