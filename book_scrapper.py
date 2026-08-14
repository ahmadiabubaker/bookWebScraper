"""Extract and Transform stages of the ETL pipeline.

EXTRACT is fetching raw HTML from books.toscrape.com and discovering which
pages exist. TRANSFORM is turning that HTML into a flat dictionary with one
consistent set of keys per book.

The LOAD stage lives in main.py, which is what writes the results to disk.
Keeping Load out of this module means these functions can be reused for a
different destination later without touching the scraping logic.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_soup(url, session=requests):
    """EXTRACT: fetch one page and hand back a parsed soup object.

    Every network read in the pipeline funnels through here, so the timeout
    and the error check are written once rather than at each call site.
    """
    response = session.get(url, timeout=10)
    response.raise_for_status()  # turn a 404 or 500 into an exception instead of parsing an error page
    return BeautifulSoup(response.content, "html.parser")

def scrape_book(url, session=requests):
    """TRANSFORM: turn one book's product page into a single flat record.

    This is where the real transform work happens. The page holds the same
    facts in several different shapes, so each field needs its own rule to
    get at it, and every book has to come out with identical keys so the
    rows line up in the CSV later.
    """
    soup = get_soup(url, session)  # EXTRACT: the one network read for this book

    title = soup.find("h1").get_text(strip=True)

    # Category is not labelled anywhere, it is only implied by the book's
    # position in the breadcrumb trail: Home > Books > Category > Title.
    # Index 2 is the category. Guard the length in case the trail is shorter.
    breadcrumb_items = soup.find("ul", class_="breadcrumb").find_all("li")
    category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) > 2 else None

    # Rating is encoded as a CSS class, not as text: class="star-rating Three".
    # Index 0 is "star-rating", so index 1 is the word we want.
    rating = soup.find("p", class_="star-rating")["class"][1]

    # The description is a sibling of the heading div rather than inside it.
    # Some books have no description at all, so this has to tolerate a miss.
    desc_div = soup.find("div", id="product_description")
    description = desc_div.find_next_sibling("p").get_text(strip=True) if desc_div else None

    # Image src is relative ("../../media/cache/..."), which is useless once
    # it leaves this page. urljoin resolves it against the page URL to make
    # an absolute URL the Load stage can download later.
    img_relative = soup.find("div", class_="item active").find("img")["src"]
    image_url = urljoin(url, img_relative)

    # The product table is a set of header/value row pairs. Collapsing it into
    # a dict lets the fields below be looked up by name instead of by row
    # number, which stops the mapping breaking if the site reorders rows.
    table = soup.find("table", class_="table-striped")
    rows = table.find_all("tr")
    table_data = {row.find("th").get_text(strip=True): row.find("td").get_text(strip=True) for row in rows}

    # The transformed record. These keys are the pipeline's agreed shape:
    # main.py writes them as CSV columns in this same order.
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
    """EXTRACT: walk every page of one category and transform each book on it.

    A category can run across several pages, so this follows the "next" link
    until there is not one, which is the point where the category is finished.
    """
    all_books = []
    while url:
        soup = get_soup(url, session=session)

        # Each listing tile only carries a summary, so follow its link and
        # transform the full product page instead of the tile.
        for book in soup.find_all("article", class_="product_pod"):
            link = urljoin(url, book.find("a")["href"])
            all_books.append(scrape_book(link, session=session))

        # Look for a next page. Absent on the last page, which ends the loop.
        next_link = soup.find("li", class_="next")
        url = urljoin(url, next_link.find("a")["href"]) if next_link else None
    return all_books



def scrape_all_books(url, session=requests):
    """EXTRACT: the top of the pipeline, covering every category on the site.

    Returns the full list of transformed records, ready for the Load stage.
    """
    soup = get_soup(url, session=session)

    # The sidebar nav is the only listing of categories. If the site's markup
    # changes, fail loudly here rather than silently scraping zero books.
    nav = soup.find("ul", class_="nav nav-list")
    if nav is None:
        raise ValueError("Category nav not found, page structure may have changed")

    # Skip the first link, which is the "Books" catch-all covering everything
    # and would double count every book.
    categories = nav.find_all("a")[1:]

    all_books = []
    for category in categories:
        category_url = urljoin(url, category["href"])
        all_books.extend(scrape_category(category_url, session=session))
    return all_books
