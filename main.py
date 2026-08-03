import csv
import os
import requests
from urllib.parse import urlparse

from scraper import scrape_all_books

def download_image(image_url, category, session=requests):
    folder = os.path.join("images", category or "uncategorized")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.basename(urlparse(image_url).path)
    filepath = os.path.join(folder, filename)

    response = session.get(image_url, timeout=10)
    response.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(response.content)
    return filepath

def main():
    base_url = "https://books.toscrape.com/"
    fieldnames = ["product_page_url", "universal_product_code", "book_title",
                  "price_including_tax", "price_excluding_tax", "quantity_available",
                  "product_description", "category", "review_rating", "image_url"]

    os.makedirs("data", exist_ok=True)

    with requests.Session() as session:
        books = scrape_all_books(base_url, session=session)

        with open(os.path.join("data", "book_data.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)

        for book in books:
            download_image(book["image_url"], book["category"], session=session)

if __name__ == "__main__":
    main()