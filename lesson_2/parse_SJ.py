import json
import os
import pprint

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost')
db = client.parse_vacancy
super_j = db.super_j

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': '*/*'
}
params = {
    'page': 1,
}


def get_pagin(url):
    response = requests.get(url=url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'lxml')
    pagination = int(soup.find_all('div', class_='e495U')[-1].find_all('a')[-2].find('span', class_='_1BOkc').getText())
    count = int(
        input(
            f"По данной вакансии найдено {pagination} страниц\nВведите кол-ва страниц, которые хотите просмотреть: "))
    return count


def get_data(url, count):
    print("Please wait...")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    res_list = list()
    for page in range(1, count + 1):
        response = requests.get(url=url, headers=headers, params=params)
        soup = BeautifulSoup(response.text, 'lxml')

        block_v = soup.find_all('div', class_='f-test-search-result-item')
        for vacancy in block_v:
            info = vacancy.find('div', class_='jNMYr')

            try:
                title = info.find('a').getText().strip()
                link = info.find('a').get('href')
                price = info.find('span', class_='_2Wp8I').text
                company = info.find_next_sibling('div').find('span').getText()
                # print(company)

                tmp = price.replace('\xa0', '')
                mini_max = tmp[0:-4].replace('—', ' ').split(' ')
                currency = tmp[-4:]

                if mini_max[0].startswith('По'):
                    min_price = 'по договоренности'
                    max_price = ''
                    currency = 'руб.'
                elif mini_max[0].startswith('от'):
                    min_price = mini_max[0].replace('от', '')
                    max_price = ''
                elif mini_max[0].startswith('до'):
                    max_price = mini_max[0].replace('до', '')
                    mix_price = ''
                elif mini_max[0].isdigit():
                    min_price = mini_max[0]
                    max_price = ''
                else:
                    min_price, max_price = mini_max

                salary = {
                    'min_price': min_price,
                    'max_price': max_price,
                    'currency': currency,
                }

                for key, value in salary.items():
                    try:
                        salary[key] = int(value)
                    except ValueError:
                        pass

            except AttributeError as e:
                title = ''
                link = ''

            if title and link:
                vacancy_dict = {
                    'title': title,
                    'salary': salary,
                    'link': f'https://russia.superjob.ru/{link}',
                    'company': company,
                    'assets': 'superjob.ru'
                }
                res_list.append(vacancy_dict)

                # INSERT
                if super_j.find_one(vacancy_dict):
                    continue
                else:
                    super_j.insert_one(vacancy_dict)
    # pprint.pprint(res_list)




def get_info():
    user_answer = int(input('Какую минимальную зп вы желаете: '))
    for doc in super_j.find({'salary.min_price': {'$gt': user_answer}}):
        salary = doc.get("salary")
        print(
            f"Должность: {doc.get('title')}\nЗарплата от {salary.get('min_price')} до {salary.get('max_price')}\n"
            f"Валюта: {salary.get('currency')}\n"
            f"Ссылка на вакансию: {doc.get('link')}")
        print('#' * 20)


def main():
    user_answer = input('Введите название вакансии: ')
    url = f'https://russia.superjob.ru/vacancy/search/?keywords={user_answer.replace(" ", "%20")}'
    count = get_pagin(url)
    get_data(url, count)
    get_info()


if __name__ == '__main__':
    main()
