# Plant Scraper

A Python application for scraping plant information from [The Old Farmer's Almanac](https://www.almanac.com/gardening/growing-guides).

## Project Overview

This project scrapes detailed plant information from The Old Farmer's Almanac website, processes the data, and provides tools to sync it to a Notion database and manage related GitHub issues.

### Key Features

- Scrape basic plant information (name, link, image URL)
- Scrape detailed plant information (growing instructions, pests/diseases, etc.)
- Preserve table formatting for pests/diseases section
- Extract recipe links
- Clean advertisement content and filter user comments
- GitHub integration for issue management
- Notion integration for storing and sharing plant data

## Documentation

Comprehensive documentation is available in the `docs/project_guide` directory:

- [Project Instructions](docs/project_guide/project_instructions.md) - Detailed guide to the project
- [Quick Reference](docs/project_guide/quick_reference.md) - Concise overview for quick reference
- [Code Examples](docs/project_guide/code_examples.md) - Practical code examples
- [Troubleshooting Guide](docs/project_guide/troubleshooting_guide.md) - Solutions to common issues

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/niklas-joh/plantScraper.git
   cd plantScraper
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your Notion API key, database ID, and GitHub info
   ```

## Quick Start

### Running the Scraper

```bash
# Run both scrapers
python scripts/run_scraper.py

# Run only the list scraper
python scripts/run_scraper.py --type list

# Run only the details scraper with a limit of 5 plants
python scripts/run_scraper.py --type details --limit 5
```

### Syncing to Notion

```bash
# Sync all plants to Notion
python scripts/sync_to_notion_requests.py

# Sync a limited number of plants
python scripts/sync_to_notion_requests.py --limit 10
```

## Project Structure

```
plantScraper/
├── data/                  # Directory for storing scraped data
├── docs/                  # Documentation
│   └── project_guide/     # Comprehensive project documentation
├── output/                # Output directory for processed data
├── scripts/               # Command-line scripts
├── src/                   # Source code
│   ├── config.py          # Centralized configuration
│   ├── github/            # GitHub integration
│   ├── notion/            # Notion integration
│   ├── processors/        # Data processing modules
│   ├── scraper/           # Scraper modules
│   └── utils/             # Utility modules
└── tests/                 # Test directory
```

For a more detailed explanation of the project structure, see the [Project Instructions](docs/project_guide/project_instructions.md).

## Common Issues

- **Bell Peppers "Wit and Wisdom" Issue**: The "Wit and Wisdom" field for Bell Peppers is stored as a dictionary in the `plants_detailed.json` file, while the Notion API expects a string.

- **Cooking Notes User Comments**: The "Cooking Notes" field may contain user comments that should be filtered out. The `filter_user_comments_from_cooking_notes()` function in `content_cleaner.py` handles this.

For more troubleshooting information, see the [Troubleshooting Guide](docs/project_guide/troubleshooting_guide.md).

## Development

### GitHub Workflow Guidelines

When working on this project:

- Always create a new branch when working on an issue from GitHub
- Include detailed git commit messages that reference issue numbers
- Close issues when they are resolved
- Keep files and folders clean and organized
- Create simple solutions and avoid over-engineering
- Follow the KISS (Keep It Simple, Stupid) approach

For more detailed guidelines, see the [Project Instructions](docs/project_guide/project_instructions.md#github-workflow-guidelines).

### Adding a New Scraper

To add a new scraper:

1. Create a new module in the `src/scraper` directory
2. Extend the `BaseScraper` class
3. Implement the `scrape` and `process_data` methods

For code examples, see the [Code Examples](docs/project_guide/code_examples.md) document.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
