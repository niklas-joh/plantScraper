# Plant Scraper Quick Reference Guide

## Project Purpose
A Python application that scrapes plant information from [The Old Farmer's Almanac](https://www.almanac.com/gardening/growing-guides), processes the data, and syncs it to a Notion database.

## Key Components

### 1. Scraper Modules
- **PlantListScraper**: Scrapes basic plant info (name, link, image URL)
- **PlantDetailsScraper**: Scrapes detailed plant info (growing instructions, pests/diseases, etc.)

### 2. Data Processing
- **content_cleaner.py**: Cleans and formats scraped content
  - Removes advertisements, filters user comments, extracts recipe links

### 3. Notion Integration
- **sync_to_notion_requests.py**: Syncs plant data to Notion database

### 4. GitHub Integration
- Tools for managing issues and updates

## Common Commands

### Run the Scraper
```bash
python scripts/run_scraper.py [--type {list,details,all}] [--limit LIMIT]
```

### Sync to Notion
```bash
python scripts/sync_to_notion_requests.py [--limit LIMIT]
```

### Create GitHub Issues
```bash
python scripts/create_issue_with_gh_cli.py
```

## Data Flow
1. **Scrape**: Extract plant data from website
2. **Process**: Clean and format the data
3. **Store**: Save to CSV (basic info) and JSON (detailed info)
4. **Sync**: Upload to Notion database

## Common Issues
- **Bell Peppers "Wit and Wisdom" Issue**: Field stored as dictionary but Notion expects string
- **Cooking Notes User Comments**: Need to filter out user comments

## GitHub Workflow Guidelines
- **Branch Management**: Always create a new branch for GitHub issues
- **Commit Messages**: Include detailed messages that reference issue numbers
- **Issue Management**: Close issues when resolved
- **Code Quality**:
  - Keep files and folders clean
  - Reuse content when possible
  - Create simple solutions (KISS approach)
  - Avoid hard coding unless explicitly permitted
  - Separate responsibilities between modules

## Environment Variables
- `NOTION_API_KEY`: Notion API key
- `NOTION_DATABASE_ID`: Notion database ID
- `GITHUB_OWNER`: GitHub repository owner
- `GITHUB_REPO`: GitHub repository name

## Key Files
- `scripts/run_scraper.py`: Main script to run the scraper
- `scripts/sync_to_notion_requests.py`: Sync data to Notion
- `src/processors/content_cleaner.py`: Clean and format content
- `src/scraper/plant_details.py`: Scrape detailed plant information
- `output/plants_detailed.json`: Detailed plant data
