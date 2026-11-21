"""Scrape the latest Mars news, images, weather, facts and hemisphere images.

Each section is scraped independently: if one source is unavailable or has
changed its layout, that section is left empty and the others still load.
"""
import logging
import time

import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser

log = logging.getLogger(__name__)

NEWS_URL = "https://mars.nasa.gov/news/"
JPL_BASE_URL = "https://www.jpl.nasa.gov"
JPL_IMAGES_URL = JPL_BASE_URL + "/spaceimages/?search=&category=Mars"
WEATHER_URL = "https://twitter.com/marswxreport?lang=en"
FACTS_URL = "https://space-facts.com/mars/"
USGS_BASE_URL = "https://astrogeology.usgs.gov"
HEMISPHERES_URL = USGS_BASE_URL + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


def get_soup(browser, url, wait=1):
    """Visit a page, give its JavaScript time to render, and parse it."""
    browser.visit(url)
    time.sleep(wait)
    return BeautifulSoup(browser.html, "html.parser")


def scrape_news(browser):
    """Return (title, teaser) of the latest NASA Mars news article."""
    soup = get_soup(browser, NEWS_URL, wait=3)
    slide = soup.find("li", class_="slide")
    title = slide.find("div", class_="content_title").text.strip()
    teaser = slide.find("div", class_="article_teaser_body").text.strip()
    return title, teaser


def scrape_featured_image(browser):
    """Return the full-size URL of JPL's featured Mars image."""
    soup = get_soup(browser, JPL_IMAGES_URL)
    return JPL_BASE_URL + soup.find("a", class_="button fancybox")["data-fancybox-href"]


def scrape_weather(browser):
    """Return the text of the latest InSight weather tweet."""
    soup = get_soup(browser, WEATHER_URL, wait=10)
    # Twitter has used both markups for tweet text
    candidates = soup.find_all("p", class_="TweetTextSize") or soup.find_all(
        "span", class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0"
    )
    for tweet in candidates:
        if "InSight" in tweet.text:
            text = tweet.text
            if tweet.a is not None:  # drop the trailing pic.twitter.com link
                text = text.replace(tweet.a.text, "")
            return text.strip()
    return ""


def scrape_facts():
    """Return the Mars facts table as an HTML string."""
    for df in pd.read_html(FACTS_URL):
        if df.shape[1] >= 2:
            df = df.iloc[:, :2]
            df.columns = ["Description", "Value"]
            return df.set_index("Description").to_html(classes="table table-striped").replace("\n", "")
    return ""


def scrape_hemispheres(browser):
    """Return [{'title': ..., 'img_url': ...}] for the four Mars hemispheres."""
    soup = get_soup(browser, HEMISPHERES_URL)
    pages = [
        (item.find("h3").text.strip(), USGS_BASE_URL + item.find("a")["href"])
        for item in soup.find_all("div", class_="item")
    ]

    hemispheres = []
    for title, page_url in pages:
        page = get_soup(browser, page_url)
        img_url = USGS_BASE_URL + page.find("img", class_="wide-image")["src"]
        hemispheres.append({"title": title, "img_url": img_url})
    return hemispheres


def _safely(section, func, default):
    """Run one scraping step; log and return a default if the source fails."""
    try:
        return func()
    except Exception as exc:  # a source changing its layout should not stop the others
        log.warning("Could not scrape %s: %s", section, exc)
        return default


def scrape(headless=True):
    """Scrape every source and return one document for MongoDB."""
    with Browser("chrome", headless=headless) as browser:
        news_title, news_p = _safely("news", lambda: scrape_news(browser), ("", ""))
        return {
            "news_title": news_title,
            "news_p": news_p,
            "featured_image_url": _safely("featured image", lambda: scrape_featured_image(browser), ""),
            "mars_weather": _safely("weather", lambda: scrape_weather(browser), ""),
            "marsfacts_html": _safely("facts", scrape_facts, ""),
            "hemisphere_image_urls": _safely("hemispheres", lambda: scrape_hemispheres(browser), []),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from pprint import pprint

    pprint(scrape())
