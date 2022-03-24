# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Lesson6Item(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    old_price = scrapy.Field()
    curr_price = scrapy.Field()
    rate = scrapy.Field()
    link = scrapy.Field()
    _id = scrapy.Field()

