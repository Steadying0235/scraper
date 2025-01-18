# +
import requests
from bs4 import BeautifulSoup

url = 'https://www.nature.com/search?q=machine+learning&article_type=research&subject=medical-research&date_range=2022-2025&order=date_desc'
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.select("ul.app-article-list-row > li.app-article-list-row__item")

    for article in articles:
            title = article.select_one("h3.c-card__title > a.c-card__link").text.strip()
            link = article.select_one("h3.c-card__title > a.c-card__link")["href"]
            # Ensure the link is a full URL
            full_link = f"https://www.nature.com{link}" if not link.startswith("http") else link
            date = article.select_one("time.c-meta__item").text.strip()

            # Print the extracted details
            print(f"Title: {title}")
            print(f"Link: {full_link}")
            print(f"Publication Date: {date}")
            print("-" * 80)
    else:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
