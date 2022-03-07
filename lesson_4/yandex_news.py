import os
from pprint import pprint

from requests import Session
from lxml import html
from pymongo import MongoClient
from time import sleep

client = MongoClient('localhost', 27017)
db = client.news
yandex_news = db.yandex_news

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'
}


def get_data(url):
    with Session() as session:
        response = session.get(url=url, headers=headers)
        dom = html.fromstring(response.text)
        sections = dom.xpath("//section")
        for block_news in sections:
            news = block_news.xpath(".//div[contains(@class,'mg-grid__item')]")
            for item in news:
                # title = item.xpath(".//h2[@class='mg-card__title']//text()")
                link = item.xpath(".//a[@class='mg-card__link']/@href")[0]
                time = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]
                id_db = link.split('/')[-1]
                source_link, source, title = get_news(link, session)
                sleep(0.3)

                data_news = {
                    '_id': id_db,
                    'title': title.replace('\xa0', ' '),
                    'source': source,
                    'source_link': source_link,
                    'link': link,
                    'time': time,
                }

                yandex_news.insert_one(data_news)


def get_news(url, session):
    response = session.get(url=url, headers=headers)
    dom = html.fromstring(response.text)
    try:
        source_link = dom.xpath(".//h1[@class='mg-story__title']/a/@href")[0]
        source = dom.xpath(".//a[@class='news-story__subtitle']/@aria-label")[0]
        title = dom.xpath(".//a[@class='mg-story__title-link']/text()")[0]
    except IndexError:
        source_link = 'error'
        source = 'error'
        title = 'error'
    return source_link, source, title


def main():
    print('Please wait...')
    url = 'https://yandex.ru/news/'
    get_data(url=url)
    for doc in yandex_news.find({}):
        pprint(doc)


if __name__ == "__main__":
    main()
