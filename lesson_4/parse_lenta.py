import re
from datetime import datetime
from pprint import pprint

from lxml import html
from pymongo import MongoClient
from requests import Session

client = MongoClient('localhost', 27017)
db = client.news
lenta_news = db.lenta_news

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'
}


def get_news(url):
    with Session() as session:
        response = session.get(url=url, headers=headers)
        dom = html.fromstring(response.text)

        blocks_news = dom.xpath("//div[@class='topnews__column']//a")
        for news in blocks_news:
            news_link = news.xpath("./@href")
            time = news.xpath(".//time/text()")[0]

            heads = news.xpath(".//div[@class='card-mini__text' or @class='card-big__titles']")
            title = heads[0].xpath(".//span/text()")
            if not title:
                title = heads[0].xpath(".//h3/text()")
            title = title[0]

            if news_link[0].startswith('https'):
                link = news_link[0]
                pattern = r'(\d{2}\-){2}\d{4}'
                date_str = re.search(pattern, link).group(0)
            else:
                link = url + news_link[0]
                pattern = r'\d{4}(\/\d{2}){2}'
                dt = re.search(pattern, link).group(0)
                _tmp = dt.split('/')
                _tmp.reverse()
                date_str = '-'.join(_tmp)
            date = datetime.strptime(date_str, '%d-%m-%Y')

            data_dict = {
                'title': title,
                'link': link,
                'date': date,
                'time': time
            }

            insert_db(data_dict)


def insert_db(data: dict):
    id_db = data.get('link').split('news')[-1] + data.get('time')
    title = data.get('title')
    link = data.get('link')
    date = data.get('date')

    data_news = {
        '_id': id_db,
        'title': title,
        'link': link,
        'date': date
    }

    lenta_news.insert_one(data_news)


def main():
    url = 'https://lenta.ru'
    get_news(url=url)
    for doc in lenta_news.find({}):
        pprint(doc)


if __name__ == "__main__":
    main()
