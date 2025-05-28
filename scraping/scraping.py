import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

# MongoDB setup
client = MongoClient('mongodb+srv://fatihfernando01:123@cluster0.4kz97zw.mongodb.net/')
db = client['berita']
collection = db['hoax_teridentifikasi']

# Fungsi untuk membaca URL dari file hoax.txt
def read_hoax_links(file_path):
    with open(file_path, 'r') as file:
        links = file.readlines()
    return [link.strip() for link in links]

# Fungsi untuk scraping artikel dari link
def scrape_article(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(f"Error fetching {url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ambil title
        title_tag = soup.find('h1', class_='entry-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        # Ambil body dari entry-content (BUKAN td-post-content)
        content_div = soup.find('div', class_='entry-content')
        if content_div:
            paragraphs = content_div.find_all(['p', 'li'])
            body = ' '.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            body = 'No body content'

        timestamp = datetime.now()

        return {"title": title, "url": url, "body": body, "timestamp": timestamp}

    except Exception as e:
        print(f"Error while scraping {url}: {e}")
        return None

# Fungsi utama untuk crawling dan menyimpan data
def crawl_and_save_data(file_path):
    links = read_hoax_links(file_path)

    for link in links:
        article_data = scrape_article(link)
        if article_data:
            # Simpan data ke MongoDB
            collection.update_one(
                {"url": article_data["url"]},
                {"$set": article_data},
                upsert=True  # Jika URL sudah ada, update data
            )
            print(f"Disimpan: {article_data['title']} - {article_data['url']}")

# Memulai crawling dan menyimpan hasil
if __name__ == "__main__":
    hoax_links_file = 'hoax.txt'
    crawl_and_save_data(hoax_links_file)
