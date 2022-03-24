# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import os
from lesson6.spiders import LabirintSpider, Book24Spider


class Lesson6Pipeline:
    client = MongoClient('localhost', 27017)
    path, name_db = os.path.split(os.path.abspath(os.path.dirname(__file__)))
    mongo_db = client[name_db]

    def process_item(self, item, spider):
        if spider.name == LabirintSpider.name:
            try:
                _id = item.get('link').split("/")[-2]
                item['_id'] = _id
                item['old_price'] = int(item.get('old_price'))
                item['rate'] = float(item.get('rate'))
                item['curr_price'] = int(item.get('old_price'))
            except ValueError:
                pass
        elif spider.name == Book24Spider.name:
            try:
                _id = item.get("link").split("-")[-1]
                item['_id'] = _id
                item['old_price'] = int(item.get('old_price').replace("\xa0", ""))
                item['curr_price'] = int(item.get('old_price').replace("\xa0", ""))
                item['rate'] = float(item.get('rate'))
            except ValueError:
                pass
        else:
            raise Exception("неизвестный паук")

        collection = self.mongo_db[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            collection.replace_one({"_id": item.get("_id")}, item)
        return item

