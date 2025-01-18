import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL with page placeholder
base_url = "https://www.nature.com/search?q=machine+learning&order=date_desc&subject=medical-research&article_type=research&date_range=2022-2025&page={}"

# Headers to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

# Function to extract article details from a single page
def extract_articles(soup):
    articles_data = []
    articles = soup.select("ul.app-article-list-row > li.app-article-list-row__item")

    for article in articles:
        # Extract title, link, and date
        title = article.select_one("h3.c-card__title > a.c-card__link").text.strip()
        link = article.select_one("h3.c-card__title > a.c-card__link")["href"]
        full_link = f"https://www.nature.com{link}" if not link.startswith("http") else link
        date = article.select_one("time.c-meta__item").text.strip()

        # Fetch the abstract from the article's page
        abstract = fetch_abstract(full_link)

        # Append the data as a dictionary
        articles_data.append({
            "title": title,
            "link": full_link,
            "publication_date": date,
            "abstract": abstract
        })
    return articles_data

# Function to fetch the abstract from an article page
def fetch_abstract(article_url):
    try:
        response = requests.get(article_url, headers=headers)
        if response.status_code == 200:
            article_soup = BeautifulSoup(response.text, "html.parser")
            abstract_tag = article_soup.select_one("div.c-article-section__content p")
            if abstract_tag:
                return abstract_tag.text.strip()
        return "Abstract not available"
    except Exception as e:
        return f"Error fetching abstract: {e}"

# Main function to scrape all pages
def scrape_all_pages(start_page, end_page):
    all_articles = []

    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")
        current_page_url = base_url.format(page)
        response = requests.get(current_page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract articles from the current page
        all_articles.extend(extract_articles(soup))

        # Be polite and avoid overwhelming the server
        time.sleep(1)

    return all_articles

# Start scraping
articles = scrape_all_pages(start_page=1, end_page=36)

# Save the data to a JSON file
with open("nature_articles.json", "w", encoding="utf-8") as json_file:
    json.dump(articles, json_file, ensure_ascii=False, indent=4)

print(f"Scraping completed. {len(articles)} articles saved to 'nature_articles.json'.")
