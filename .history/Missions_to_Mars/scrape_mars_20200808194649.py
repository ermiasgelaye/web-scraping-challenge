# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import urllib.parse
import pymongo
import pprint
import pandas as pd
import time
# Initialize browser
def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    #executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    news_title = soup.find('div', class_ = 'content_title').text
    news_p = soup.find('div', class_ = 'article_teaser_body').text
    date = soup.find('div', class_='list_date').text
   
   # Retrieve the parent divs for all latest news
    results = soup.find_all('div', class_='list_text')
   # loop over results to get list
    for result in results:
        # scrape the news title
        news_title = result.find('div', class_='content_title').text
    
        # scrape the news  paragraph
        news_p = result.find('div', class_='article_teaser_body').text
    
        # scrape article posted date 
        date = result.find('div', class_='list_date').text
    post = {'header': news_title,
    'subheader': news_p,
    'date': date
    }
    return post
    
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    base_url = 'https://www.jpl.nasa.gov'
    featured_image =soup.find("a", class_ = "button fancybox")["data-fancybox-href"]
    featured_image_url = base_url + featured_image

    url = ('https://twitter.com/marswxreport?lang=en')
    browser.visit(url)
    time.sleep(3)
    html = browser.html
    soup = bs(html, 'html.parser')
    mars_weather = soup.find('p', class_ = 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text.strip()

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
        link = result.find('a', class_ = "itemLink product-item")
        link_text = link['href']
        hemispheres_url = base_url + link_text
        sites.append(hemispheres_url)
    hemispheres = []
    for site in sites:
        browser.visit(site)
        html = browser.html
        soup = bs(html, 'html.parser')
        title = soup.find('h2', class_ = "title").text.strip()
        url = soup.find_all('a', target = "_blank", href = True)[0]['href']
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
