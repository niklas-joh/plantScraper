# Plant Scraper

A Python application for scraping plant information from [The Old Farmer's Almanac](https://www.almanac.com/gardening/growing-guides).

## Project Structure

```
plantScraper/
├── data/                  # Directory for storing scraped data
├── docs/                  # Documentation
├── output/                # Output directory for processed data
├── scripts/               # Command-line scripts
│   ├── comment_on_issue.py
│   ├── run_scraper.py
│   └── update_github_issue.py
├── src/                   # Source code
│   ├── config.py          # Centralized configuration
│   ├── github/            # GitHub integration
│   │   ├── create_issues.py
│   │   ├── issue_manager.py
│   │   ├── token_manager.py
│   │   └── update_issue_secure.py
│   ├── processors/        # Data processing modules
│   │   └── content_cleaner.py
│   ├── scraper/           # Scraper modules
│   │   ├── base.py
│   │   ├── plant_details.py
│   │   └── plant_list.py
│   └── utils/             # Utility modules
│       ├── file_io.py
│       └── http.py
└── tests/                 # Test directory
```

## Features

- Scrape basic plant information (name, link, image URL)
- Scrape detailed plant information (growing instructions, pests/diseases, etc.)
- Preserve table formatting for pests/diseases section
- Extract recipe links
- Clean advertisement content
- GitHub integration for issue management

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

## Usage

### Running the Scraper

To run the scraper, use the `run_scraper.py` script:

```
python scripts/run_scraper.py [--type {list,details,all}] [--limit LIMIT] [--output-dir OUTPUT_DIR]
```

Options:
- `--type`: Type of scraper to run (list, details, or all). Default is "all".
- `--limit`: Limit the number of plants to scrape.
- `--output-dir`: Output directory for scraped data.

Examples:
```
# Run both scrapers
python scripts/run_scraper.py

# Run only the list scraper
python scripts/run_scraper.py --type list

# Run only the details scraper with a limit of 5 plants
python scripts/run_scraper.py --type details --limit 5

# Specify a custom output directory
python scripts/run_scraper.py --output-dir custom_output
```

### GitHub Integration

#### Creating Issues

To create GitHub issues, use the `create_issues.py` module:

```python
from src.github.create_issues import create_issues

# Create issues from a JSON file
create_issues(json_file_path="path/to/issues.json")

# Create default issues
create_issues()
```

#### Commenting on Issues

To comment on a GitHub issue, use the `comment_on_issue.py` script:

```
python scripts/comment_on_issue.py ISSUE_NUMBER [--file FILE] [--owner OWNER] [--repo REPO]
```

#### Updating Issues

To update a GitHub issue, use the `update_github_issue.py` script:

```
python scripts/update_github_issue.py ISSUE_NUMBER {comment,update} [--file FILE] [--owner OWNER] [--repo REPO]
```

## Configuration

Configuration settings are centralized in `src/config.py`. You can modify this file to change:

- Base URLs for scraping
- HTTP headers
- Request timeout and delay
- GitHub repository information
- File paths for data storage

## Development

### Adding a New Scraper

To add a new scraper:

1. Create a new module in the `src/scraper` directory
2. Extend the `BaseScraper` class
3. Implement the `scrape` and `process_data` methods

Example:
```python
from src.scraper.base import BaseScraper

class MyNewScraper(BaseScraper):
    def scrape(self, url):
        # Implementation
        pass
        
    def process_data(self, data):
        # Implementation
        pass
```

### Testing

Run tests using pytest:

```
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
