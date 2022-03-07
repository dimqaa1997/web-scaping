from datetime import datetime
from pprint import pprint
from time import sleep

from lxml import html
from pymongo import MongoClient
from requests import Session

client = MongoClient('localhost', 27017)
db = client.news
mail_news = db.mail_news

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'
}


def get_news(url):
    with Session() as session:
        response = session.get(url=url, headers=headers)
        dom = html.fromstring(response.text)

        blocks_news = dom.xpath("//ul[contains(@class, 'list_type_square')]")
        for block in blocks_news:
            link_news = block.xpath(".//li[contains(@class,'list__item')]//@href")
            for link in link_news:
                get_data(session, link)
                # без этого не собирает все данные
                sleep(0.5)


def get_data(session, link):
    response = session.get(url=link, headers=headers)
    dom = html.fromstring(response.text)
    data = {
        'title': dom.xpath(".//h1//text()"),
        'date': dom.xpath(".//span[@datetime]/@datetime"),
        'source': dom.xpath(".//a[contains(@class,'color_gray')]//text()"),
        'source_link': dom.xpath(".//a[contains(@class,'color_gray')]/@href"),
    }
    insert_db(data, link)


def insert_db(data: dict, link):
    id_db = data.get('date')[0] + str(link).strip('/').split('/')[-1]
    dt = datetime.fromisoformat(str(data.get('date')[0]))
    date = dt.strftime('%d.%m.%Y %H:%M:%S')
    title = data.get('title')[0]
    news_link = link
    try:
        source = data.get('source')[0]
        source_link = data.get('source_link')[0]
    except IndexError:
        source = 'источник не указан'
        source_link = 'нет ссылки на источник'
    data_news = {
        '_id': id_db,
        'title': title,
        'news_link': news_link,
        'source': source,
        'source_link': source_link,
        'date': date
    }
    # pprint(data_news)

    mail_news.insert_one(data_news)


def main():
    print('Please wait...')
    url = 'https://news.mail.ru/'
    get_news(url=url)
    for doc in mail_news.find({}):
        pprint(doc)


if __name__ == '__main__':
    main()
