import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL for pagination
base_url = "https://www.nature.com"

# Search URL
search_url = f"{base_url}/search?q=machine+learning&order=date_desc&subject=medical-research&article_type=research&date_range=2022-2025&page=1"
# search_url = f"{base_url}/search?q=machine+learning&order=date_desc&subject=medical-research&article_type=research&date_range=2022-2025"

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
        full_link = f"{base_url}{link}" if not link.startswith("http") else link
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

# Function to find the total number of pages
def get_total_pages(soup):
    pagination_links = soup.select("li.c-pagination__item > a.c-pagination__link")
    if pagination_links:
        last_page = pagination_links[-1].get("href").split("page=")[-1]
        return int(last_page)
    return 1

def get_next_page_url(soup):
    next_page_tag = soup.select_one("li.c-pagination__item > a.c-pagination__link[rel='next']")
    if next_page_tag:
        next_page_url = next_page_tag["href"]
        # Return the full URL if the next page link is relative
        return f"{base_url}{next_page_url}" if not next_page_url.startswith("http") else next_page_url
    return None


def scrape_all_pages(start_url):
    current_page_url = start_url
    all_articles = []
    page = 1

    while current_page_url:
        print(f"Scraping page {page}... URL: {current_page_url}")
        response = requests.get(current_page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract articles from the current page
        articles = extract_articles(soup)
        all_articles.extend(articles)

        # Find the next page URL
        current_page_url = get_next_page_url(soup)
        page += 1
        time.sleep(1)  # Be polite and avoid overwhelming the server

    return all_articles

# Start scraping
articles = scrape_all_pages(search_url)

# Save the data to a JSON file
with open("nature_articles.json", "w", encoding="utf-8") as json_file:
    json.dump(articles, json_file, ensure_ascii=False, indent=4)

print(f"Scraping completed. {len(articles)} articles saved to 'nature_articles.json'.")
