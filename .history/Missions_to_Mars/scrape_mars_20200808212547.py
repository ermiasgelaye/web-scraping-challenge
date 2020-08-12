# Dependencies
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser

# Initialize browser


def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    #executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    news_title = soup.find('div', class_='content_title').text
    news_p = soup.find('div', class_='article_teaser_body').text

    url = 'https://www.jpl.nasa.gov/spaceimages/'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    base_url = 'https://www.jpl.nasa.gov'
    image_url = soup.find("a", class_="button fancybox")["data-fancybox-href"]
    featured_image_url = base_url + image_url

    _url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(mars_weather_url)
    html = browser.html
    soup = bs(html, "html.parser")
    mars_tweets = [soup.find_all('p', class_="TweetTextSize"),soup.find_all(
        'span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")]

    for tweets in mars_tweets:
        mars_tweet = tweets

    for tweet in mars_tweet:
        if 'InSight' in tweet.text:
            mars_weather = tweet.text
            if tweet.a in tweet:
                mars_weather = mars_weather.strip(tweet.a.text)
            break

    url = 'https://space-facts.com/mars/'
    browser.visit(url)
    tables = pd.read_html(url)
    facts_df = tables[0]
    facts_df.columns = ['Fact', 'Value']
    facts_df['Fact'] = facts_df['Fact'].str.replace(':', '')
    facts_df.reset_index(drop=True, inplace=True)
    facts_html = facts_df.to_html()

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    results = soup.find_all('div', class_="description")
    base_url = 'https://astrogeology.usgs.gov/'
    sites = []
    for result in results:
        link = result.find('a', class_="itemLink product-item")
        link_text = link['href']
        hemispheres_url = base_url + link_text
        sites.append(hemispheres_url)
    hemispheres = []
    for site in sites:
        browser.visit(site)
        html = browser.html
        soup = bs(html, 'html.parser')
        title = soup.find('h2', class_="title").text.strip()
        url = soup.find_all('a', target="_blank", href=True)[0]['href']
        hemispheres.append({"title": title, "img_url": url})

    output = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather": mars_weather,
        "facts_html": facts_html,
        "hemispheres": hemispheres
    }
    return output

