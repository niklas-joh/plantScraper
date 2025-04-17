@echo off
py -3.12 -m pip install "./packages/numpy-1.26.4-cp312-cp312-win_amd64.whl"
py -3.12 -m pip install "./packages/pandas-2.1.4-cp312-cp312-win_amd64.whl"
py -3.12 -m pip install "./packages/charset_normalizer-3.4.1-py3-none-any.whl"
py -3.12 -m pip install "./packages/urllib3-2.4.0-py3-none-any.whl"
py -3.12 -m pip install "./packages/certifi-2025.1.31-py3-none-any.whl"
py -3.12 -m pip install "./packages/idna-3.10-py3-none-any.whl"
py -3.12 -m pip install --no-deps "./packages/requests-2.32.3-py3-none-any.whl"
py -3.12 -m pip install "./packages/beautifulsoup4-4.13.4-py3-none-any.whl"
py -3.12 plants_detailed_scraper_refactored.py 