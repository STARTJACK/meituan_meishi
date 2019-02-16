# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MeituanMeishiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    classify = scrapy.Field()
    address = scrapy.Field()
    avgPrice = scrapy.Field()
    avgScore = scrapy.Field()
    name = scrapy.Field()
    serviceTags = scrapy.Field()
    phone = scrapy.Field()
    openTime = scrapy.Field()
    city = scrapy.Field()
    areas = scrapy.Field()
    # level = scrapy.Field()
    # companyName = scrapy.Field()
    # licenseNo = scrapy.Field()
    # legalRepresentitive = scrapy.Field()
    # validDate = scrapy.Field()
    evaluateNumber = scrapy.Field()
    tags = scrapy.Field()
    # scope = scrapy.Field()
    source = scrapy.Field()
