import json
import os

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.parse_vacancy
hh = db.hh

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'
}
params = {
    'page': 0,
    'items_on_page': 20
}


def get_pagination(url):
    response = requests.get(url=url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'lxml')
    pagin = int(soup.find('div', class_='pager').find_all('span', recursive=False)[-1].find('a').find('span').getText())
    count = int(
        input(f"По данной вакансии найдено {pagin} страницю\nВведите кол-ва страниц, которые хотите просмотреть: "))
    return count


def get_data(url, count):
    res_list = list()

    for page in range(0, count):
        params['page'] = page
        src = requests.get(url=url, headers=headers, params=params)
        soup = BeautifulSoup(src.text, 'lxml')
        block_vacancy = soup.find('div', class_='vacancy-serp').find_all('div', class_='vacancy-serp-item')
        print(len(block_vacancy))
        for block in block_vacancy:
            title = block.find('a').getText()
            link = block.find('a').get('href')
            company = block.find('div', class_="vacancy-serp-item__meta-info-company").find('a').getText()
            try:
                price = block.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().replace(' –',
                                                                                                                '')
                _temp = price.split(' ')
            except AttributeError as e:
                # print('зп не указана')
                _temp = None
            finally:
                if _temp:
                    if _temp[0] == 'от':
                        min_price, max_price, currency = _temp
                        min_price = max_price.replace('\u202f', '')
                        max_price = 'не указана'
                    elif _temp[0] == 'до':
                        min_price = 'не указана'

                    else:
                        min_price, max_price, currency = _temp
                    salary = {
                        'min_price': min_price.replace('\u202f', ''),
                        'max_price': max_price.replace('\u202f', ''),
                        'currency': currency
                    }

                    for key, value in salary.items():
                        try:
                            salary[key] = int(value)
                        except ValueError:
                            pass

                else:
                    salary = {
                        'min_price': 'не указана',
                        'max_price': 'не указана',
                        'currency': 'не указана'
                    }

                data_dict = {
                    'title': title,
                    'salary': salary,
                    'link': link,
                    'company': company,
                    'assets': 'hh.ru'
                }
                res_list.append(data_dict)

                # INSERT
                if hh.find_one(data_dict):
                    continue
                else:
                    hh.insert_one(data_dict)


def get_info():
    user_answer = int(input('Какую минимальную зп вы желаете: '))
    for doc in hh.find({'salary.min_price': {'$gt': user_answer}}):
        salary = doc.get("salary")
        print(
            f"Должность: {doc.get('title')}\nЗарплата от {salary.get('min_price')} до {salary.get('max_price')}\n"
            f"Валюта: {salary.get('currency')}\n"
            f"Ссылка на вакансию: {doc.get('link')}")
        print('#' * 20)


def main():
    user_answer = input('Введите вакансию: ').replace(" ", "+")
    url = f'https://hh.ru/search/vacancy?text=={user_answer}'
    count = get_pagination(url=url)
    get_data(url, count)
    get_info()


if __name__ == '__main__':
    main()
