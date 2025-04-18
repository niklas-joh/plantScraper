# Plant Scraper Scripts

This directory contains utility scripts for the Plant Scraper project.

## Available Scripts

### Plant Scraper

- **run_scraper.py** - Main script to run the plant scraper
  - Supports scraping plant lists and plant details
  - Can limit the number of plants to scrape
  - Allows specifying custom output directories

### GitHub Issue Management

- **update_github_issue.py** - Update GitHub issues or add comments
  - Securely manages GitHub tokens
  - Supports reading content from files or stdin
  - Can update issue body or add comments

- **create_issue_with_gh_cli.py** - Create GitHub issues using GitHub CLI
  - Uses the GitHub CLI for better security and integration
  - Automatically creates labels if they don't exist
  - Specifically designed for the Notion integration issue

### Notion Integration

- **sync_to_notion.py** - Synchronize plants data to Notion database
  - Currently a placeholder that will be implemented once the Notion integration is approved
  - Will support synchronizing plant data to a Notion database

### Maintenance

- **cleanup.py** - Utility script to clean up redundant files
  - Removes files with overlapping functionality
  - Maintains a clean scripts directory

## Usage Examples

### Running the Plant Scraper

```bash
# Run both list and details scrapers
python scripts/run_scraper.py

# Run only the list scraper
python scripts/run_scraper.py --type list

# Run only the details scraper
python scripts/run_scraper.py --type details

# Limit the number of plants to scrape
python scripts/run_scraper.py --limit 10

# Specify a custom output directory
python scripts/run_scraper.py --output-dir ./custom_output
```

### Managing GitHub Issues

```bash
# Add a comment to an issue
python scripts/update_github_issue.py 123 comment --file comment.md

# Update an issue body
python scripts/update_github_issue.py 123 update --file new_body.md

# Create the Notion integration issue
python scripts/create_issue_with_gh_cli.py
```

### Notion Integration (Future)

```bash
# Synchronize plants data to Notion
python scripts/sync_to_notion.py --api-key your_api_key --database-id your_database_id
```

## Development Notes

- All scripts use the project's main modules from the `src` directory
- Scripts are designed to be run from the project root directory
- Most scripts support command-line arguments for flexibility
