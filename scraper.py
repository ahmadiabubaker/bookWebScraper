import requests
from bs4 import BeautifulSoup, soup
from urllib.parse import urljoin

def get_soup(url, session=requests):
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.content, "html.parser")

def scrape_book(url, session=requests):
    soup = get_soup(url, session)

    title = soup.find("h1").get_text(strip=True)

    breadcrumb_items = soup.find("ul", class_="breadcrumb").find_all("li")
    category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) > 2 else None

    rating = soup.find("p", class_="star-rating")["class"][1]

    desc_div = soup.find("div", id="product_description")
    description = desc_div.find_next_sibling("p").get_text(strip=True) if desc_div else None
    img_relative = soup.find("div", class_="item active").find("img")["src"]
    image_url = urljoin(url, img_relative)

    table = soup.find("table", class_="table-striped")
    rows = table.find_all("tr")
    table_data = {row.find("th").get_text(strip=True): row.find("td").get_text(strip=True) for row in rows}

    return {
        "product_page_url": url,
        "universal_product_code": table_data.get("UPC"),
        "book_title": title,
        "price_including_tax": table_data.get("Price (incl. tax)"),
        "price_excluding_tax": table_data.get("Price (excl. tax)"),
        "quantity_available": table_data.get("Availability"),
        "product_description": description,
        "category": category,
        "review_rating": rating,
        "image_url": image_url
    }



def scrape_category(url, session=requests):
    all_books = []
    while url:
        soup = get_soup(url, session=session)
        for book in soup.find_all("article", class_="product_pod"):
            link = urljoin(url, book.find("a")["href"])
            all_books.append(scrape_book(link, session=session))
        next_link = soup.find("li", class_="next")
        url = urljoin(url, next_link.find("a")["href"]) if next_link else None
    return all_books



def scrape_all_books(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    nav = soup.find("ul", class_="nav nav-list")
    if nav is None:
        raise ValueError("Category nav not found, page structure may have changed")

    categories = nav.find_all("a")[1:]
    all_books = []
    for category in categories:
        category_url = urljoin(url, category["href"])
        books_in_category = scrape_category(category_url)
        all_books.extend(books_in_category)
    return all_books
