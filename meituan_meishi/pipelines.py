# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from twisted.enterprise import adbapi
import pymysql
import copy

MYSQL_DB = 'meituan'
MYSQL_HOST = '127.0.0.1'#'120.79.177.168'#
MYSQL_PORT = '3306'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''

class MySQLPipeline(object):

    def open_spider(self,spider):
        self.dbpool = adbapi.ConnectionPool('pymysql',
                                            host=MYSQL_HOST,
                                            database=MYSQL_DB,
                                            user=MYSQL_USER,
                                            password=MYSQL_PASSWORD,)

    def close_spider(self,spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        asynItem = copy.deepcopy(item)
        self.dbpool.runInteraction(self.insert_db, asynItem)
        return item

    def insert_db(self, tx, item):
        data = (
            item['classify'],
            item['address'],
            item['avgPrice'],
            item['avgScore'],
            item['name'],
            item['serviceTags'],
            item['phone'],
            item['openTime'],
            item['city'],
            item['areas'],
            item['evaluateNumber'],
            item['tags'],
            item['source'],
        )
        values = ', '.join(["%s"]*len(item))
        sql_query = 'INSERT IGNORE INTO meituan_meishi (classify, address, avgPrice, avgScore, name, serviceTags, phone, openTime, city, areas, evaluateNumber, tags, source) values (%s)'%values
        tx.execute(sql_query, data)

