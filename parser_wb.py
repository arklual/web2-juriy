from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup as BS
import time


def parse(url):
    try:
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(5)
        response = driver.page_source
        driver.close()
        soup = BS(response)
        name = soup.find('h1', {'class': 'product-page__title'}).text
        img = soup.find('img', {'class': 'photo-zoom__preview'}).get('src')
        price = int(soup.find('ins', {'class': 'price-block__final-price'}).text.replace('\xa0', '').replace('₽', '').strip())
        return {
            'name': name,
            'url': url,
            'img': img,
            'price': price
        }
    except:
        return None

