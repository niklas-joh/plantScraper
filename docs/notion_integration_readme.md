# Notion Integration for Plant Scraper

This feature allows you to export plant data from the Plant Scraper project to a Notion database, providing a more user-friendly and collaborative way to work with the plant information.

## Overview

The Notion integration enables you to:

- Export plant data from `plants_detailed.json` to a Notion database
- Maintain a structured view of plant information in Notion
- Easily filter, sort, and search plant data
- Share plant information with team members
- Access plant data from mobile devices through the Notion app

## Prerequisites

- A Notion account
- Admin access to create integrations in your Notion workspace
- Python 3.6+
- The `notion-client` Python package (will be added to requirements.txt when implemented)

## Setup

1. **Create a Notion Integration**
   - Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Name it "Plant Scraper Integration"
   - Select your workspace
   - Set appropriate capabilities (Read content, Update content, Insert content)
   - Copy the "Internal Integration Token"

2. **Create a Notion Database**
   - Create a new page in your Notion workspace
   - Add a database (full page)
   - Configure the database with the properties listed in the [Database Schema](#database-schema) section
   - Share the database with your integration by clicking "Share" and selecting your integration
   - Copy the database ID from the URL (the part after the workspace name and before the question mark)

3. **Set Environment Variables**
   - Set `NOTION_API_KEY` to your integration token
   - Set `NOTION_DATABASE_ID` to your database ID

## Usage

You can use the integration with the following command:

```bash
python scripts/sync_to_notion_requests.py
```

Optional arguments:
- `--api-key`: Override the Notion API key from environment variable
- `--database-id`: Override the Notion database ID from environment variable
- `--plants-file`: Specify a custom path to the plants JSON file
- `--limit`: Limit the number of plants to sync

Example:
```bash
python scripts/sync_to_notion_requests.py --limit 10
```

## Database Schema

The Notion database will have the following properties:

| Property Name | Property Type | Description |
|---------------|---------------|-------------|
| Name | Title | Plant name |
| Botanical Name | Text | Scientific name |
| Plant Type | Select | Type of plant (Vegetable, Herb, etc.) |
| Sun Exposure | Multi-select | Light requirements |
| Soil pH | Select | Soil pH preference |
| Bloom Time | Multi-select | When the plant blooms |
| Flower Color | Multi-select | Color of flowers |
| Hardiness Zone | Multi-select | USDA hardiness zones |
| Link | URL | Link to plant page on The Old Farmer's Almanac |
| Image URL | URL | Link to plant image |
| Photo Credit | Text | Image attribution |

Additionally, the following information will be included in the page content:
- Planting instructions
- Growing information
- Harvesting details
- Pests/Diseases table
- Recipes
- Wit and Wisdom
- Cooking Notes

## Implementation Status

This feature is currently in the planning stage. A GitHub issue has been created to track the implementation progress.

See the [detailed technical documentation](notion_integration.md) for implementation details.
