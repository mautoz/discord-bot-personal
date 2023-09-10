#!/usr/bin/env python3
import itertools
from tools.screenshot import get_screenshots
import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

HEADERS = {
    'User-Agent': 'Your User-Agent String',  # Replace with a user agent string
    'Accept-Language': 'en-US,en;q=0.5',     # Specify the desired language
}
url = os.getenv("SCREENSHOT_LINK")

response = requests.get(url, headers=HEADERS, timeout=5)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    main_content_sections = soup.find_all('section', class_='main-content')

    links = []
    for section in main_content_sections:
        h2_element_last = section.find('h2', text='Últimas notícias')
        h2_element_plus = section.find('h2', text='Mais notícias')

        if h2_element_last or h2_element_plus:
            article_links = []
            article_tags = section.find_all('article', class_='card-post -rowdesktop')

            for article_tag in article_tags:
                if article_tag.a and article_tag.a.has_attr('href'):
                    href = article_tag.a['href']
                    article_links.append(href)
                else:
                    logging.warning("No 'href' attribute found in this article tag.")

            links.append(article_links)
    
    links = list(itertools.chain.from_iterable(links))
    logging.info("Links were collected")

else:
    logging.error("Failed to retrieve the web page. Status code: %s", response.status_code)

if links:
    get_screenshots(links=links)
else:
    logging.warning("Links list was empty!")
