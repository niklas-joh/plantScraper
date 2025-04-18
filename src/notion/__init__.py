"""
Notion integration package for the Plant Scraper project.

This package provides functionality to synchronize plant data with a Notion database.

DEPRECATED: This package is deprecated and will be removed in a future version.
Please use scripts/sync_to_notion_requests.py instead, which provides all the
functionality in a single script.
"""

import warnings

# Emit a deprecation warning
warnings.warn(
    "The src.notion package is deprecated and will be removed in a future version. "
    "Please use scripts/sync_to_notion_requests.py instead.",
    DeprecationWarning,
    stacklevel=2
)
