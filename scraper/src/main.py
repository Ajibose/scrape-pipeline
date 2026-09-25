import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin


def read_page(file_path, current_page):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

        soup = BeautifulSoup(content, "html.parser")
        result = soup.select("h3 a")

        next_link = soup.select_one("li.next a")
        next_page = urljoin(current_page, next_link["href"])   

        return (result, next_page)


def process_tags(tags, current_page):
    books_details = []
    for tag in tags:
        book_url = urljoin(current_page, tag["href"])
        books_details.append(book_url)
    
    return books_details

def process_page(file_path, current_page):
    books_discovered = 0

    tags, next_page = read_page(file_path, current_page)
    if len(tags) > 0:
        book_urls = process_tags(tags, current_page)

    return {"book_urls": book_urls, "next_page": next_page}


def main():
    current_page = "http://books.toscrape.com/"
    is_previous_fetch = False
    books = []

    for i in range(3):
        file_path = Path("../cache") / f"catalogue-page-{i+1}.html"
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                is_previous_fetch = False
                print("CACHE HIT")
                print(len(file.read()))

            page = process_page(file_path, current_page)
        except FileNotFoundError:
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if is_previous_fetch:
                time.sleep(0.5)
            
            headers = {"User-Agent": "FlyRankInternshipA9/1.0 (https://github.com/Ajibose/scrape-pipeline)"}
            response = requests.get(current_page, headers=headers, timeout=10)

            print(current_page)
            if response.status_code != 200:
                print(f"Failed to fetch catalogue in iteration {i+1}")
                continue

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(response.text)
                    
            print("FETCH")
            print(len(response.text))

            page = process_page(file_path, current_page)

            is_previous_fetch = True
        
        books.extend(page["book_urls"])
        current_page = page["next_page"]

    discovered = len(books)
    unique_books = set(books)
    unique_urls = len(unique_books)

    print(f"catalogue_pages=3, discovered={discovered} , unique_urls={unique_urls}")
    print("urls: ", books)

if __name__ == '__main__':
    main()
