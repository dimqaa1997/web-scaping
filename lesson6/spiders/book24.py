import re

import scrapy
from scrapy.http import HtmlResponse

from lesson6.items import Lesson6Item


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = []

    def parse(self, response: HtmlResponse):
        pattern = re.compile(r"page\-\d*")
        count = 2
        while True:
            if response.status != 200:
                break
            if re.search(pattern, response.url):
                new_page = re.sub(pattern, f"page-{count}", response.url)
            else:
                new_page = f"https://book24.ru/search/page-{count}/{response.url.split('/')[-1]}"
            yield response.follow(new_page, callback=self.parse)
            count += 1

            links = response.xpath("//div[@class='product-card__image-holder']/a/@href")
            for link in links:
                yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        title = response.xpath("//h1/text()").get()
        rates = response.xpath("//span[@class='rating-widget__main-text']/text()").get()
        author = response.xpath("//a[contains(@class, 'product-characteristic-link')]/text()").get()
        curr_price = response.xpath("//span[contains(@class, 'product-sidebar-price__price')]/text()").get()
        old_price = response.xpath("//span[contains(@class, 'product-sidebar-price__price-old')]/text()").get()
        if not old_price:
            old_price = "нет скидки на товар"

        yield Lesson6Item(title=title, author=author, old_price=old_price, curr_price=curr_price, rate=rates, link=link)

    @classmethod
    def set_start_urls(cls, value):
        cls.start_urls = value
