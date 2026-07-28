import requests
from bs4 import BeautifulSoup

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
category = book_soup.find("ul", class_="breadcrumb").find_all("li")[2].string
description = book_soup.find("div", id="product_description").find_next_sibling("p").string
table = book_soup.find("table", class_="table-striped")
rows = table.find_all("td")
upc = rows[0].string
price_excl_tax = rows[2].string
price_incl_tax = rows[3].string
quantity_available = rows[5].string
print(upc)
print(price_excl_tax)
print(price_incl_tax)
print(quantity_available)
print(category)
print(description)

print(price)
print(title)
print(rating)
print(link)
