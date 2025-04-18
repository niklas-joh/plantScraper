# Plant Scraper Project Instructions

## Project Overview

The Plant Scraper is a Python application designed to scrape plant information from [The Old Farmer's Almanac](https://www.almanac.com/gardening/growing-guides). The project has several key components:

1. **Scraper Modules**: Extract plant data from the website
2. **Data Processing**: Clean and format the scraped data
3. **Notion Integration**: Sync plant data to a Notion database
4. **GitHub Integration**: Manage issues and updates related to the project

## Project Structure

```
plantScraper/
├── data/                  # Directory for storing scraped data
│   └── plants.csv         # Basic plant information (name, link, image URL)
├── docs/                  # Documentation
│   ├── github_cli_auth.md
│   ├── notion_integration_readme.md
│   └── notion_integration.md
├── output/                # Output directory for processed data
│   └── plants_detailed.json # Detailed plant information
├── scripts/               # Command-line scripts
│   ├── cleanup.py
│   ├── create_issue_with_gh_cli.py
│   ├── create_notion_database.py
│   ├── run_scraper.py     # Main script to run the scraper
│   ├── sync_to_notion_requests.py # Sync data to Notion
│   ├── update_github_issue.py
│   └── update_notion_database.py
├── src/                   # Source code
│   ├── config.py          # Centralized configuration
│   ├── github/            # GitHub integration
│   │   ├── create_issues.py
│   │   ├── issue_manager.py
│   │   ├── token_manager.py
│   │   └── update_issue_secure.py
│   ├── notion/            # Notion integration
│   │   ├── client.py
│   │   ├── config.py
│   │   ├── schema.py
│   │   ├── sync.py        # Deprecated, use scripts/sync_to_notion_requests.py instead
│   │   └── transformer.py
│   ├── processors/        # Data processing modules
│   │   └── content_cleaner.py # Clean and format scraped content
│   ├── scraper/           # Scraper modules
│   │   ├── base.py        # Base scraper functionality
│   │   ├── plant_details.py # Scrape detailed plant information
│   │   └── plant_list.py  # Scrape basic plant information
│   └── utils/             # Utility modules
│       ├── file_io.py     # File I/O operations
│       └── http.py        # HTTP request utilities
└── tests/                 # Test directory
    ├── test_config.py
    ├── test_file_io.py
    ├── test_http.py
    ├── test_notion_schema.py
    └── test_notion_transformer.py
```

## Key Components

### 1. Scraper Modules

The scraper is divided into two main components:

- **PlantListScraper** (`src/scraper/plant_list.py`): Scrapes basic plant information (name, link, image URL) from the main growing guides page and saves it to a CSV file.
- **PlantDetailsScraper** (`src/scraper/plant_details.py`): Scrapes detailed plant information (growing instructions, pests/diseases, etc.) for each plant in the CSV file and saves it to a JSON file.

Both scrapers extend the `BaseScraper` class (`src/scraper/base.py`), which provides common functionality like HTTP requests, content extraction, and table processing.

### 2. Data Processing

The `content_cleaner.py` module (`src/processors/content_cleaner.py`) provides functions for cleaning and formatting the scraped content:

- `clean_content()`: Removes extra whitespace and newlines
- `clean_advertisement_content()`: Removes advertisement text from content
- `filter_user_comments_from_cooking_notes()`: Filters out user comments from Cooking Notes content
- `has_subheadings()`: Checks if a field item contains subheadings (h3 tags)
- `extract_recipe_links()`: Extracts recipe links from a field item

### 3. Notion Integration

The Notion integration allows syncing plant data to a Notion database:

- `sync_to_notion_requests.py` (`scripts/sync_to_notion_requests.py`): Main script for syncing plant data to Notion
- `transformer.py` (`src/notion/transformer.py`): Transforms plant data to Notion format
- `schema.py` (`src/notion/schema.py`): Defines the Notion database schema
- `client.py` (`src/notion/client.py`): Provides a client for interacting with the Notion API

Note: The `sync.py` module (`src/notion/sync.py`) is deprecated and has been replaced by `sync_to_notion_requests.py`.

### 4. GitHub Integration

The GitHub integration allows managing issues and updates related to the project:

- `create_issues.py` (`src/github/create_issues.py`): Creates GitHub issues
- `issue_manager.py` (`src/github/issue_manager.py`): Manages GitHub issues
- `token_manager.py` (`src/github/token_manager.py`): Manages GitHub tokens
- `update_issue_secure.py` (`src/github/update_issue_secure.py`): Updates GitHub issues securely

## Data Structure

### Plant List Data (CSV)

The plant list data is stored in a CSV file with the following columns:
- Name: Name of the plant
- Link: URL to the plant's page on The Old Farmer's Almanac
- Image URL: URL to the plant's image

### Plant Details Data (JSON)

The plant details data is stored in a JSON file with the following structure for each plant:

```json
{
  "Name": "Plant Name",
  "Link": "https://www.almanac.com/plant/plant-name",
  "Image URL": "https://www.almanac.com/sites/default/files/image_url.jpg",
  "Botanical Name": "Botanical name",
  "Plant Type": "Annual, Perennial, etc.",
  "Sun Exposure": "Full Sun, Partial Shade, etc.",
  "Soil pH": "Acidic, Neutral, Alkaline, etc.",
  "Bloom Time": "Spring, Summer, etc.",
  "Flower Color": "Red, Blue, etc.",
  "Hardiness Zone": "3-9, etc.",
  "Planting": {
    "content": "Main planting instructions",
    "sub_headings": {
      "When to Plant": "Planting time instructions",
      "How to Plant": "Planting method instructions"
    }
  },
  "Growing": {
    "content": "Main growing instructions",
    "sub_headings": {
      "Soil Requirements": "Soil information",
      "Watering": "Watering instructions"
    }
  },
  "Harvesting": {
    "content": "Main harvesting instructions",
    "sub_headings": {
      "When to Harvest": "Harvesting time instructions",
      "How to Harvest": "Harvesting method instructions"
    }
  },
  "Pests/Diseases": {
    "headers": ["Pest/Disease", "Type", "Symptoms", "Control"],
    "rows": [
      {
        "pest": "Aphids",
        "type": "Insect",
        "symptoms": "Curled leaves, stunted growth",
        "control": "Insecticidal soap, neem oil"
      }
    ]
  },
  "Wit and Wisdom": "Interesting facts about the plant",
  "Cooking Notes": "Cooking instructions and tips",
  "Recipes": {
    "Recipe Name": "https://www.almanac.com/recipe/recipe-link"
  }
}
```

Note: Some fields like "Wit and Wisdom" can be either a string or a dictionary with "content" and "sub_headings" keys. The Notion integration expects a string, so the dictionary format needs to be converted to a string before syncing to Notion.

## Common Issues and Solutions

### Bell Peppers "Wit and Wisdom" Issue

**Issue**: The "Wit and Wisdom" field for Bell Peppers is stored as a dictionary in the `plants_detailed.json` file, while the Notion API expects a string.

**Solution**: Two approaches were implemented:

1. `fix_bell_peppers_wit_wisdom.py`: Converts the dictionary to a properly formatted string in the `plants_detailed.json` file.
2. `fix_notion_sync_script.py`: Modifies the `sync_to_notion_requests.py` script to handle both string and dictionary formats for the "Wit and Wisdom" field.

### Cooking Notes User Comments

**Issue**: The "Cooking Notes" field contains user comments that should be filtered out.

**Solution**: The `filter_user_comments_from_cooking_notes()` function in `content_cleaner.py` filters out user comments from the "Cooking Notes" content.

## Usage Instructions

### Running the Scraper

To run the scraper, use the `run_scraper.py` script:

```bash
python scripts/run_scraper.py [--type {list,details,all}] [--limit LIMIT] [--output-dir OUTPUT_DIR]
```

Options:
- `--type`: Type of scraper to run (list, details, or all). Default is "all".
- `--limit`: Limit the number of plants to scrape.
- `--output-dir`: Output directory for scraped data.

### Syncing to Notion

To sync plant data to a Notion database, use the `sync_to_notion_requests.py` script:

```bash
python scripts/sync_to_notion_requests.py [--api-key API_KEY] [--database-id DATABASE_ID] [--plants-file PLANTS_FILE] [--limit LIMIT]
```

Options:
- `--api-key`: Override the Notion API key from environment variable
- `--database-id`: Override the Notion database ID from environment variable
- `--plants-file`: Specify a custom path to the plants JSON file
- `--limit`: Limit the number of plants to sync

### GitHub Integration

To create GitHub issues, use the `create_issue_with_gh_cli.py` script:

```bash
python scripts/create_issue_with_gh_cli.py
```

To update GitHub issues, use the `update_github_issue.py` script:

```bash
python scripts/update_github_issue.py ISSUE_NUMBER {comment,update} [--file FILE] [--owner OWNER] [--repo REPO]
```

## Environment Variables

The project uses the following environment variables:

- `NOTION_API_KEY`: Notion API key
- `NOTION_DATABASE_ID`: Notion database ID
- `GITHUB_OWNER`: GitHub repository owner
- `GITHUB_REPO`: GitHub repository name

These can be set in a `.env` file in the project root directory.

## Development Guidelines

### GitHub Workflow Guidelines

When working on this project, follow these guidelines for GitHub workflow:

1. **Branch Management**:
   - Always create a new branch when working on an issue from GitHub
   - Use descriptive branch names that reference the issue number (e.g., `fix-issue-42-bell-peppers`)

2. **Commit Messages**:
   - Include detailed git commit messages that clearly explain the changes
   - Reference the issue number in commit messages (e.g., "Fix #42: Resolved Bell Peppers Wit and Wisdom issue")
   - Follow the format: "type(scope): message" (e.g., "fix(notion): handle dictionary format in Wit and Wisdom field")

3. **Issue Management**:
   - Close issues when they are resolved
   - Reference the commit or PR that resolves the issue

4. **Code Quality**:
   - Keep files and folders clean and organized
   - Reuse content whenever possible to avoid duplication
   - Create simple solutions and avoid over-engineering
   - Do not hard code values unless explicitly permitted
   - Think of holistic solutions that consider the entire system
   - Follow the KISS (Keep It Simple, Stupid) approach
   - Separate responsibilities between modules and functions

### Adding a New Scraper

To add a new scraper:

1. Create a new module in the `src/scraper` directory
2. Extend the `BaseScraper` class
3. Implement the `scrape` and `process_data` methods

### Data Processing

When processing scraped data:

1. Use the `clean_content()` function to remove extra whitespace and newlines
2. Use the `clean_advertisement_content()` function to remove advertisement text
3. Handle fields with subheadings appropriately
4. Extract recipe links using the `extract_recipe_links()` function

### Notion Integration

When syncing data to Notion:

1. Transform plant data to Notion format using the `transform_plant_to_notion_properties()` function
2. Create content blocks using the `create_plant_content_blocks()` function
3. Handle both string and dictionary formats for fields like "Wit and Wisdom"
4. Be aware of Notion's 2000 character limit for text blocks
