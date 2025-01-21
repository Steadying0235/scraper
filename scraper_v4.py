import requests
from bs4 import BeautifulSoup
import json
import time

# Base URL with page placeholder
#base_url = "https://www.nature.com/search?q=machine+learning&order=date_desc&subject=medical-research&article_type=research&date_range=2022-2025&page={}"
base_url = "https://www.nature.com/search?q=machine+learning&order=date_desc&subject=medical-research&article_type=research&date_range=2020-2022&page={}"

# Headers to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
}

# Keywords for ML techniques and security/privacy
ML_TECHNIQUES = {
    "Traditional ML": ["regression", "decision tree", "svm", "k-means"],
    "DNN": ["cnn", "rnn", "lstm", "deep learning"],
    "Gen AI": ["transformer", "gan", "diffusion model", "bert"]
}

SECURITY_PRIVACY = {
    "Attack Types": ["evasion", "poisoning", "backdoor", "membership inference", "model inversion", "data reconstruction", "untargeted poisoning", "energy latency attack"],
    "Attacker Identity": ["patient", "healthcare practitioner", "ml service provider", "3rd-party healthcare organization", "cybercriminals", "business competitors"],
    "Attacker Capability": ["training data control", "model control", "testing data control", "query access", "explanation access"]
}

# Function to classify ML techniques based on keywords
def classify_ml_techniques(text):
    techniques = []
    for category, keywords in ML_TECHNIQUES.items():
        if any(keyword in text.lower() for keyword in keywords):
            techniques.append(category)
    return techniques

# Function to identify security/privacy discussions
def identify_security_privacy(text):
    findings = {}
    for category, keywords in SECURITY_PRIVACY.items():
        findings[category] = [keyword for keyword in keywords if keyword in text.lower()]
    return findings

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

        # Fetch the abstract, conclusions, and analyze text
        abstract, conclusions, full_text = fetch_article_details(full_link)
        ml_techniques = classify_ml_techniques(full_text)
        security_privacy = identify_security_privacy(full_text)

        # Append the data as a dictionary
        articles_data.append({
            "title": title,
            "link": full_link,
            "publication_date": date,
            "abstract": abstract,
            "conclusions": conclusions,
            "ml_techniques": ml_techniques,
            "security_privacy": security_privacy
        })
    return articles_data

# Function to fetch article details (abstract, conclusions, and full text)
def fetch_article_details(article_url):
    try:
        response = requests.get(article_url, headers=headers)
        if response.status_code == 200:
            article_soup = BeautifulSoup(response.text, "html.parser")

            # Extract abstract
            abstract_tag = article_soup.select_one("div.c-article-section__content p")
            abstract = abstract_tag.text.strip() if abstract_tag else "Abstract not available"

            # Extract conclusions
            conclusions_tag = article_soup.find("h2", string=lambda text: "conclusions" in text.lower())
            conclusions = "Conclusions not available"
            if conclusions_tag:
                conclusions_section = conclusions_tag.find_next("div", class_="c-article-section__content")
                if conclusions_section:
                    conclusions = conclusions_section.text.strip()

            # Combine all text for analysis
            full_text = article_soup.get_text(separator=" ", strip=True).lower()

            return abstract, conclusions, full_text
        return "Abstract not available", "Conclusions not available", ""
    except Exception as e:
        return f"Error fetching abstract: {e}", "Conclusions not available", ""

# Main function to scrape all pages and save to individual JSON files
def scrape_all_pages(start_page, end_page):
    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")
        current_page_url = base_url.format(page)
        response = requests.get(current_page_url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract articles from the current page
        articles = extract_articles(soup)

        # Save each page's results into a separate JSON file
        with open(f"articles/nature_articles_date_range_2020_2022_page_{page}.json", "w", encoding="utf-8") as json_file:
            json.dump(articles, json_file, ensure_ascii=False, indent=4)

        # Be polite and avoid overwhelming the server
        time.sleep(2)

# Start scraping
scrape_all_pages(start_page=1, end_page=26)

print("Scraping completed. Check JSON files for each page.")
