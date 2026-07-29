import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape_book(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find("h1").string
    price = soup.find("p", class_="price_color").string
    rating = soup.find("p", class_="star-rating")["class"][1]
    category = soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").string
    description = soup.find("div", id="product_description").find_next_sibling("p").string
    table = soup.find("table", class_="table-striped")
    img_src = url  + soup.find("div", class_="item active").find("img")["src"]
    image_url = img_src.replace("../../", "")
    rows = table.find_all("td")
    upc = rows[0].string
    price_excl_tax = rows[2].string
    price_incl_tax = rows[3].string
    quantity_available = rows[5].string

    return {
        "product_page_url": url,
        "universal_product_code": upc,
        "book_title": title,
        "price_including_tax": price_incl_tax,
        "price_excluding_tax": price_excl_tax,
        "quantity_available": quantity_available,
        "product_description": description,
        "category": category,
        "review_rating": rating,
        "image_url": image_url
    }



def scrape_category(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    all_books = []
    for book in books:
        href = book.find("a")["href"]
        link = urljoin(url, href)
        book_data = scrape_book(link)
        all_books.append(book_data)

    return all_books

def scrape_all_books(url):
    ...


