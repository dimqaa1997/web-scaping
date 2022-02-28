import json
import os

import requests


def run_scraping():
    answer = input("Введите имя пользователя GitHub: ")
    url = f'https://api.github.com/users/{answer}/repos'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    response = requests.get(url=url)
    data = response.json()

    if not response.ok:
        print('Пользователь не найден')
    else:
        print('Успех')
        try:
            os.mkdir(os.path.join(BASE_DIR, 'data_github'))
            with open("data_github/data_github.json", "w", encoding="utf8") as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)
        except FileExistsError:
            with open("data_github/data_github.json", "w", encoding="utf8") as fp:
                json.dump(data, fp, indent=4, ensure_ascii=False)
        finally:
            for item in data:
                print(f"репозиторий: {item.get('name')}\nссылка: {item.get('html_url')}")
                print('#' * 20)


if __name__ == '__main__':
    run_scraping()
