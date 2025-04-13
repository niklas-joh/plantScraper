import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.almanac.com"
grid_url = f"{base_url}/gardening/growing-guides"

# Spoof browser headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

response = requests.get(grid_url, headers=headers)
print(f"Status code: {response.status_code}")

soup = BeautifulSoup(response.content, "html.parser")

# Write page HTML to a file to verify scraping worked
with open("page.html", "w", encoding="utf-8") as f:
    f.write(soup.prettify())

plants = []
plant_items = soup.select("div.views-view-grid__item")
print(f"Found {len(plant_items)} plant items")

for item in plant_items:
    title_elem = item.select_one("h3 a")
    if not title_elem:
        continue

    name = title_elem.text.strip()
    link = base_url + title_elem["href"]

    # Get image URL
    img_elem = item.select_one("img")
    img_path = img_elem.get("src") or img_elem.get("data-src", "") if img_elem else ""
    img_url = base_url + img_path if img_path.startswith("/") else img_path

    plants.append({
        "Name": name,
        "Link": link,
        "Image URL": img_url
    })

# Save to CSV
df = pd.DataFrame(plants)
df.to_csv("plants.csv", index=False)
print(f"✅ Saved {len(df)} rows to plants.csv")