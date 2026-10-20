import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from urllib.parse import urljoin
import time

def polite_fetch(url: str, headers: dict):
    time.sleep(0.5)
    response = requests.get(url, headers=headers, timeout=10)

    return response

def process_book(book_url: str, source_page: str) -> dict:
    headers = {"User-Agent": "FlyRankInternshipA9/1.0 (https://github.com/Ajibose/scrape-pipeline)"}

    file_name = f"../cache/{book_url.split("/")[-2]}.html"

    try:
        with open(file_name, "r", encoding="utf-8") as file:
            is_previous_fetch = False
            page_content = file.read() 

    except FileNotFoundError:
        response = polite_fetch(book_url, headers)

        if response.status_code != 200:
            print(f"Book Page not Found for {book_url}")
            return

        page_content = response.content.decode("utf-8")
        

        with open(file_name, "w", encoding="utf-8") as file:
            file.write(page_content)

    fetched_at = datetime.fromtimestamp(Path(file_name).stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    book_record = get_book_record(page_content, book_url, source_page)
    book_record["fetched_at"] = fetched_at

    return book_record
 

def get_book_record(page_content: str, book_url: str, source_page: str) -> dict:
    soup = BeautifulSoup(page_content, "html.parser")
    title_tag = soup.select_one(".product_page .product_main h1")

    if title_tag is None:
        print(f"Error getting title for {book_url}") 
        return

    title = title_tag.get_text(strip=True)

    price_tag = soup.select_one(".product_page .price_color")
    price = price_tag.get_text(strip=True)

    availability_tag = soup.select_one(".product_page .product_main .availability")
    availability = availability_tag.get_text(strip=True)

    rating_tag = soup.select_one(".product_page .product_main .star-rating")
    rating_classes = rating_tag.get("class")
    rating = rating_classes[-1]

    description_tag = soup.select_one(".product_page #product_description + p")
    description = None

    if description_tag is not None:
        description = description_tag.get_text()

    return {
        "title": title, "product_url": book_url, "price_text": price, 
        "availability_text": availability, "rating_text": rating,
        "description": description, "source_page": source_page
    }

def read_page(file_path, current_page):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

        soup = BeautifulSoup(content, "html.parser")
        result = soup.select("h3 a")

        next_link = soup.select_one("li.next a")
        next_page = urljoin(current_page, next_link["href"])   

        return (result, next_page)


def process_tags(tags, current_page) -> (list, list):
    page_books_record = []
    books_details = []
    for tag in tags:
        book_url = urljoin(current_page, tag["href"])
        books_details.append(book_url)

        book_record = process_book(book_url, current_page)
        page_books_record.append(book_record)
        
    return books_details, page_books_record

def process_page(file_path, current_page):
    books_discovered = 0

    tags, next_page = read_page(file_path, current_page)
    if len(tags) > 0:
        book_urls, page_books_record = process_tags(tags, current_page)

    return {"book_urls": book_urls, "next_page": next_page, "books_records": page_books_record}


def main():
    current_page = "https://books.toscrape.com/"
    is_previous_fetch = False
    books = []
    all_books_records = []

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
        all_books_records.extend(page["books_records"])

    discovered = len(books)
    unique_books = set(books)
    unique_urls = len(unique_books)

    print(f"catalogue_pages=3, discovered={discovered}, unique_urls={unique_urls}, detail_pages={len(all_books_records)}")
    print(all_books_records[20])
    # print("urls: ", books)

if __name__ == '__main__':
    main()
