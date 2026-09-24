import requests
from pathlib import Path

def main():
    file_path = Path("../cache") / "catalogue-page-1.html"
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            print("CACHE HIT")
            print(len(file.read()))
    except FileNotFoundError:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        headers = {"User-Agent": "FlyRankInternshipA9/1.0 (https://github.com/Ajibose/scrape-pipeline)"}
        response = requests.get("http://books.toscrape.com/", headers=headers, timeout=10)

        if response.status_code != 200:
            print("Failed to fetch catalogue")
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)
                
        print("FETCH")
        print(len(response.text))

if __name__ == '__main__':
    main()
