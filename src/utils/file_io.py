"""
File I/O utility functions for reading and writing data.
"""

import os
import json
import pandas as pd
from src import config

def ensure_directory_exists(directory):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path to ensure exists
    """
    os.makedirs(directory, exist_ok=True)

def save_to_csv(data, filepath=None, index=False):
    """
    Save data to a CSV file.
    
    Args:
        data (list or DataFrame): Data to save
        filepath (str, optional): Path to save the file. Defaults to config.PLANTS_CSV.
        index (bool, optional): Whether to include index in CSV. Defaults to False.
        
    Returns:
        bool: True if successful, False otherwise
    """
    filepath = filepath or config.PLANTS_CSV
    
    try:
        # Ensure the directory exists
        ensure_directory_exists(os.path.dirname(filepath))
        
        # Convert to DataFrame if it's a list
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data
            
        # Save to CSV
        df.to_csv(filepath, index=index)
        print(f"✅ Saved {len(df)} rows to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving to CSV: {str(e)}")
        return False

def save_to_json(data, filepath=None, indent=2):
    """
    Save data to a JSON file.
    
    Args:
        data (dict or list): Data to save
        filepath (str, optional): Path to save the file. Defaults to config.PLANTS_DETAILED_JSON.
        indent (int, optional): JSON indentation level. Defaults to 2.
        
    Returns:
        bool: True if successful, False otherwise
    """
    filepath = filepath or config.PLANTS_DETAILED_JSON
    
    try:
        # Ensure the directory exists
        ensure_directory_exists(os.path.dirname(filepath))
        
        # Save to JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        print(f"✅ Saved data to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving to JSON: {str(e)}")
        return False

def load_from_csv(filepath=None):
    """
    Load data from a CSV file.
    
    Args:
        filepath (str, optional): Path to the CSV file. Defaults to config.PLANTS_CSV.
        
    Returns:
        DataFrame: Loaded data or None if loading failed
    """
    filepath = filepath or config.PLANTS_CSV
    
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Loaded {len(df)} rows from {filepath}")
        return df
    except Exception as e:
        print(f"❌ Error loading from CSV: {str(e)}")
        return None

def load_from_json(filepath=None):
    """
    Load data from a JSON file.
    
    Args:
        filepath (str, optional): Path to the JSON file. Defaults to config.PLANTS_DETAILED_JSON.
        
    Returns:
        dict or list: Loaded data or None if loading failed
    """
    filepath = filepath or config.PLANTS_DETAILED_JSON
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded data from {filepath}")
        return data
    except Exception as e:
        print(f"❌ Error loading from JSON: {str(e)}")
        return None
