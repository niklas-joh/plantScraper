"""
Test package initialization.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
