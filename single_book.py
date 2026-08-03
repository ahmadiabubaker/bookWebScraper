import requests
from bs4 import BeautifulSoup
import csv
import os

url = "https://books.toscrape.com/" 

response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")
books = soup.find_all("article", class_="product_pod")
book = books[0]
title = book.find("h3").find("a")["title"]
price = book.find("p", class_="price_color").string
rating = book.find("p", class_="star-rating")["class"][1]
link = url + book.find("a")["href"]

book_response = requests.get(link)
book_soup = BeautifulSoup(book_response.content, "html.parser")
category = book_soup.find("ul", class_="breadcrumb").find_all("li")[2].find("a").string
description = book_soup.find("div", id="product_description").find_next_sibling("p").string
table = book_soup.find("table", class_="table-striped")
img_src = url  + book_soup.find("div", class_="item active").find("img")["src"]
image_url = img_src.replace("../../", "")

rows = table.find_all("td")
upc = rows[0].string
price_excl_tax = rows[2].string
price_incl_tax = rows[3].string
quantity_available = rows[5].string


os.makedirs("data", exist_ok=True)

with open(os.path.join("data", "book_data.csv"), "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["product_page_url", "universal_product_code", "book_title", "price_including_tax", "price_excluding_tax", "quantity_available", "product_description", "category", "review_rating", "image_url"])
    writer.writerow([link, upc, title, price_incl_tax, price_excl_tax, quantity_available, description, category, rating, image_url])

