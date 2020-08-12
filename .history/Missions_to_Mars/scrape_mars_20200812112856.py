from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import re

# This is for debugging

def savetofile(contents):
    file = open('_temporary.txt',"w",encoding="utf-8")
    file.write(contents)
    file.close()


def scrape():
    executable_path = {"executable_path": "chromedriver"}
    browser = Browser("chrome", **executable_path, headless=False)

    # NASA Mars News

    url = 'https://mars.nasa.gov/news/'

    browser.visit(url)
    time.sleep(3)

    html = browser.html
    soup = bs(html, 'html.parser')

    slides = soup.find_all('li', class_='slide')
    content_title = slides[0].find('div', class_='content_title')
    news_title = content_title.text.strip()

    article_teaser_body = slides[0].find('div', class_='article_teaser_body')
    news_p = article_teaser_body.text.strip()

    # JPL Mars Space Images

    base_url = 'https://www.jpl.nasa.gov'
    url = base_url + '/spaceimages/?search=&category=Mars'

    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, 'html.parser')

    featured_image_url = base_url + soup.find('a',class_='button fancybox')['data-fancybox-href']    

    # Mars Weather
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(3)
    weather_html = browser.html
    soup = bs(weather_html, "html.parser")
    # print(weathersoup.prettify())

    mars_tweets = [soup.find_all('p', class_="TweetTextSize"), soup.find_all('span', class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")]
    
    mars_weather=[]
    for tweets in mars_tweets:
        mars_tweet = tweets

    for tweet in mars_tweet:
        if 'InSight' in tweet.text:
            mars_weather = tweet.text
            if tweet.a in tweet:
                mars_weather = mars_weather.strip(tweet.a.text)
        break

    # Mars facts
    url = 'https://space-facts.com/mars/'
    browser.visit(url)  # not necessary, but added for checking the operation
    time.sleep(1)

    dfs = pd.read_html(url)
    for df in dfs:
        try:
            df = df.rename(columns={0: "Description", 1: "Value"})
            df = df.set_index("Description")
            marsfacts_html = df.to_html().replace('\n', '')
            # df.to_html('marsfacts.html') # to save to a file to test
            break
        except:
            continue
        
    # Mars Hemispheres

    base_url = 'https://astrogeology.usgs.gov'
    url = base_url + '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    browser.visit(url)
    time.sleep(1)
    html = browser.html
    soup = bs(html, 'html.parser')

    items = soup.find_all('div', class_='item')

    urls = []
    titles = []
    for item in items:
        urls.append(base_url + item.find('a')['href'])
        titles.append(item.find('h3').text.strip())

    img_urls = []
    for oneurl in urls:
        browser.visit(oneurl)
        time.sleep(1)
        html = browser.html
        soup = bs(html, 'html.parser')
        oneurl = base_url+soup.find('img',class_='wide-image')['src']
        img_urls.append(oneurl)

    hemisphere_image_urls = []

    for i in range(len(titles)):
        hemisphere_image_urls.append({'title':titles[i],'img_url':img_urls[i]})

    # Assigning scraped data to a page
    
    marspage = {}
    marspage["news_title"] = news_title
    marspage["news_p"] = news_p
    marspage["featured_image_url"] = featured_image_url
    marspage["mars_weather"] = mars_weather
    marspage["marsfacts_html"] = marsfacts_html
    marspage["hemisphere_image_urls"] = hemisphere_image_urls

    return marspage
    
