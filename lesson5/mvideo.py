from pprint import pprint
from time import sleep

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

client = MongoClient('localhost', 27017)
db = client.mvideo
m_trend = db.trend

service = Service('./chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument(
    f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")
options.add_argument('--disable-blink-features=AutomationControlled')
browser = webdriver.Chrome(options=options)
browser.implicitly_wait(20)


def get_data():
    try:
        browser.get('https://www.mvideo.ru/')

        actions = ActionChains(browser)
        body = browser.find_element(By.TAG_NAME, 'body')

        for _ in range(150):
            body.send_keys(Keys.DOWN)
        print('done')

        btn = browser.find_element(By.XPATH, "//button[@class='tab-button ng-star-inserted']")
        actions.move_to_element(btn).perform()
        btn.click()
        trend = browser.find_element(By.TAG_NAME, "mvid-shelf-group")

        titles = trend.find_elements(By.XPATH, ".//div[@class='product-mini-card__name ng-star-inserted']")
        prices = trend.find_elements(By.CLASS_NAME, 'product-mini-card__price')

        count = 0
        for product in titles:
            link = product.find_element(By.TAG_NAME, "a").get_attribute('href')
            title = product.find_element(By.XPATH, ".//a").text
            current_price = prices[count].find_element(By.CLASS_NAME, "price__main-value").text
            try:
                old_price = prices[count].find_element(By.CLASS_NAME, "price__sale-value").text
            except:
                old_price = "Нет старой цены"

            # Не удается собрать валюту
            # Пробовал XPATH, CLASS_NAME и все впустую
            # currency = prices[count].find_element(By.CLASS_NAME, "sale-value--currency").text
            currency = 'rub.'
            id_db = link.split('-')[-3:]
            price = {
                'current_price': current_price,
                'old_price': old_price
            }
            count += 1

            data_dict = {
                '_id': ''.join(id_db),
                'title': title,
                'link': link,
                'price': price,
                'currency': currency
            }

            m_trend.insert_one(data_dict)

        sleep(5)
    except Exception as e:
        print('что-то пошло не так')
        print(e)
    finally:
        browser.close()
        browser.quit()


def main():
    get_data()
    for doc in m_trend.find({}):
        pprint(doc)


if __name__ == '__main__':
    main()
