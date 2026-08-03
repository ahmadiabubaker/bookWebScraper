"""Entry point that runs the full ETL pipeline.

ETL is a way of splitting a data job into three stages:

  EXTRACT   pull raw data out of its source, as it comes, without judging it
  TRANSFORM reshape that raw data into a clean, consistent structure
  LOAD      write the finished result somewhere it will persist

Here, Extract and Transform live in scraper.py, which fetches the pages and
turns each one into a uniform dictionary. This file is the Load stage plus
the orchestration that runs the three in order.

The value of the split is that each stage can change on its own. If the site
redesigns, only Transform changes. If the output moves to a database instead
of a CSV, only Load changes.
"""

import csv
import os
import requests
from urllib.parse import urlparse

from scraper import scrape_all_books

def download_image(image_url, category, session=requests):
    """LOAD: save one cover image to disk, filed under its category.

    This one also does a small Extract of its own, since the image bytes are
    a second network fetch that the HTML scrape did not pull down.
    """
    # Group images by category so the folder layout mirrors the CSV's
    # category column. Books with no category still need somewhere to go.
    folder = os.path.join("images", category or "uncategorized")
    os.makedirs(folder, exist_ok=True)

    # Reuse the site's own filename, taking only the path so that any query
    # string on the URL does not end up in the filename.
    filename = os.path.basename(urlparse(image_url).path)
    filepath = os.path.join(folder, filename)

    # EXTRACT: fetch the raw image bytes.
    response = session.get(image_url, timeout=10)
    response.raise_for_status()

    # LOAD: write them out. "wb" because this is binary, not text.
    with open(filepath, "wb") as f:
        f.write(response.content)
    return filepath

def main():
    """Run Extract, Transform and Load in order."""
    base_url = "https://books.toscrape.com/"

    # The agreed column order for the CSV. These names match the keys that
    # scrape_book returns, which is what lets DictWriter line them up.
    fieldnames = ["product_page_url", "universal_product_code", "book_title",
                  "price_including_tax", "price_excluding_tax", "quantity_available",
                  "product_description", "category", "review_rating", "image_url"]

    # The folder is committed to git but its contents are not, so on a fresh
    # clone it may be missing. Create it before the Load stage needs it.
    os.makedirs("data", exist_ok=True)

    # One Session for the whole run. It keeps the TCP connection open between
    # requests instead of reopening it for each of the thousand-plus fetches.
    with requests.Session() as session:
        # EXTRACT and TRANSFORM: crawl the site and get back clean records.
        books = scrape_all_books(base_url, session=session)

        # LOAD, part one: every record as a row of the CSV. DictWriter maps
        # each dictionary key to its column, so order in the dict is irrelevant.
        with open(os.path.join("data", "book_data.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)

        # LOAD, part two: the cover images. This runs after the CSV so that
        # the text data is safely on disk before the slower image downloads.
        for book in books:
            download_image(book["image_url"], book["category"], session=session)

if __name__ == "__main__":
    main()
