import author as author
import scrapy
from scrapy.http import HtmlResponse
from lesson6.items import Lesson6Item


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = []

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//div[@class='pagination-next']//@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@class='cover']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.book_parser)

    def book_parser(self, response: HtmlResponse):
        link = response.url
        title = response.xpath("//h1/text()").get()
        authors = response.xpath("//div[@class='authors']/a/text()").get()
        rate = response.xpath("//div[@id='rate']/text()").get()
        price = response.xpath("//div[@class='buying']")
        base_price = price.xpath("./div[@class='buying-price']//span[@class='buying-price-val-number']/text()").get()
        sale_price = "скидка отсутсвует"
        if not base_price:
            base_price = price.xpath(
                "./div[@class='buying-priceold']//span[@class='buying-priceold-val-number']/text()").get()
            sale_price = price.xpath(
                "./div[@class='buying-pricenew']//span[@class='buying-pricenew-val-number']/text()").get()

        yield Lesson6Item(title=title, author=authors, old_price=base_price, curr_price=sale_price, rate=rate,
                          link=link)

    @classmethod
    def set_start_urls(cls, value):
        cls.start_urls = value
