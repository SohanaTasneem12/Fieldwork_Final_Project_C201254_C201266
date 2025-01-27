from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
from db_connection import create_db_connection
from news_db_manager import execute_query, execute_read_query
from datetime import datetime


def scrape_homepage_for_links(page, max_scrolls):
    """
    Scroll the homepage a limited number of times and extract news links.
    """
    news_links = set()  # Use a set to avoid duplicate links

    for _ in range(max_scrolls):
        time.sleep(2)
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all('a', href=True):
            href = link['href']
            if "/economy/bazaar/" in href:
                full_link = href if href.startswith("http") else f"https://www.tbsnews.net{href}"
                news_links.add(full_link)
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

    return list(news_links)


def get_reporters(soup):
    """
    Extract the reporters' names from the BeautifulSoup object.

    Parameters
    ----------
    soup : BeautifulSoup
        The BeautifulSoup object containing the parsed HTML of the news article.

    Returns
    -------
    list
        A list of reporters' names.
    """
    reporters = []

    # Example of finding reporter names, adjust this to match the structure of the website
    reporter_tag = soup.find('div', class_='author')  # Change this to the actual class or tag containing reporter names
    if reporter_tag:
        reporters = [reporter_tag.get_text(strip=True)]  # Assuming there's one reporter. If multiple, adjust accordingly.

    return reporters



def scrape_news_details(page, url):
    """
    Scrape details of a single news article.
    """
    try:
        print(f"Scraping: {url}")
        page.goto(url, timeout=120000)
        page.wait_for_load_state('domcontentloaded', timeout=60000)
        page.wait_for_selector("h1[itemprop='headline']", state="attached", timeout=60000)

        content = page.content()
        soup = BeautifulSoup(content, "html.parser")

        publisher_website = url.split('/')[2]
        publisher = publisher_website.split('.')[-2]
        title_element = soup.find('h1', itemprop='headline')
        title = title_element.text.strip() if title_element else "No Title Found"
        reporter_elements = get_reporters(soup)  # Get multiple reporters
        date_element = soup.find('div', class_='author-section').find('div', class_='date')
        news_datetime = date_element.text.strip() if date_element else "No Date Found"

        # Convert the news_datetime to a valid MySQL format
        try:
            news_datetime = datetime.strptime(news_datetime, '%d %B, %Y, %I:%M %p').strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            news_datetime = "0000-00-00 00:00:00"  # Set to a default value if the conversion fails

        image_element = soup.find('picture', class_='ratio ratio__16x9')
        img_tag = image_element.find('img') if image_element else None
        image_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else "No Image Found"
        news_body = '\n'.join(p.text.strip() for p in soup.find_all('p') if p.text.strip())

        return {
            "Publisher Website": publisher_website,
            "Publisher": publisher,
            "Title": title,
            "Reporters": ", ".join(reporter_elements),  # Join multiple reporters into a single string
            "News Datetime": news_datetime,
            "News Body": news_body,
            "Image URL": image_url,
            "Link": url
        }

    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return None



def insert_data_into_database(connection, news_data):
    """
    Insert the scraped news data into the database.
    """
    try:
        # Ensure publisher exists and get publisher ID
        publisher_query = f"""
        INSERT IGNORE INTO publishers (name, email) VALUES (%s, %s);
        """
        execute_query(connection, publisher_query, (news_data["Publisher"], news_data["Publisher Website"]))

        publisher_id_query = f"SELECT id FROM publishers WHERE name = %s;"
        publisher_id = execute_read_query(connection, publisher_id_query, (news_data["Publisher"],))
        if not publisher_id:
            print(f"Error: Publisher '{news_data['Publisher']}' not found.")
            return

        # Insert news details (with the full reporter string)
        news_query = f"""
        INSERT INTO news (category_id, publishers_id, reporters, datetime, title, body, link)
        VALUES (NULL, %s, %s, %s, %s, %s, %s);
        """
        execute_query(connection, news_query, (
            publisher_id[0][0],  # Publisher ID
            news_data["Reporters"],  # Use the full reporter string
            news_data["News Datetime"],
            news_data["Title"],
            news_data["News Body"],
            news_data["Link"]
        ))

        # Insert image details
        image_query = f"""
        INSERT INTO images (news_id, image_url)
        VALUES (
            (SELECT id FROM news WHERE title = %s),
            %s
        );
        """
        execute_query(connection, image_query, (news_data["Title"], news_data["Image URL"]))

        print("Data inserted successfully.")

    except Exception as e:
        print(f"Error inserting data into the database: {e}")


def main(url, max_scrolls, max_news):
    try:
        connection = create_db_connection()
        if connection is None:
            print("Database connection failed. Exiting.")
            return

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            print(f"Navigating to homepage: {url}")
            page.goto(url, timeout=120000)

            news_links = scrape_homepage_for_links(page, max_scrolls)
            print(f"Found {len(news_links)} news links.")

            news_links = news_links[:max_news]
            for news_url in news_links:
                news_data = scrape_news_details(page, news_url)
                if news_data:
                    insert_data_into_database(connection, news_data)

            browser.close()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    homepage_url = "https://www.tbsnews.net/economy/bazaar"
    max_scrolls_to_perform = 2
    max_news_to_scrape = 5

    main(homepage_url, max_scrolls_to_perform, max_news_to_scrape)
