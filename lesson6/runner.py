from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor

from lesson6 import settings
from lesson6.spiders import LabirintSpider, Book24Spider

# Не удается обоих сразу запустить таким образом
def start_spider():
    config = Settings()
    config.setmodule(settings)

    crawler_process = CrawlerProcess(settings=config)
    crawler_process.crawl(LabirintSpider)
    crawler_process.crawl(Book24Spider)

    crawler_process.start()


def set_urls():
    user_answer = input("Введите через запятую категории или книги, которые будем искать: ")
    search_list_labirint = list(
        map(lambda item: f"https://www.labirint.ru/search/{item.strip().replace(' ', '%')}/?stype=0",
            user_answer.split(",")))

    search_list_book24 = list(map(lambda item: f"https://book24.ru/search/page-1/?q={item.strip().replace(' ', '%')}",
                                  user_answer.split(",")))

    LabirintSpider.set_start_urls(search_list_labirint)
    Book24Spider.set_start_urls(search_list_book24)


def spider_starter():
    config = Settings()
    config.setmodule(settings)

    crawl_runner = CrawlerRunner(settings=config)
    crawl_runner.crawl(LabirintSpider)
    crawl_runner.crawl(Book24Spider)

    d = crawl_runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()


if __name__ == '__main__':
    set_urls()
    spider_starter()

