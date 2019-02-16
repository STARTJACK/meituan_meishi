# -*- coding: utf-8 -*-
import scrapy
import json
import re
import copy
from .areaObj import areaObj
from .cityId import cityId
from ..items import MeituanMeishiItem
from scrapy_redis.spiders import RedisSpider

# class MeishiSpider(scrapy.Spider):
class MeishiSpider(RedisSpider):
    name = 'meishi'
    allowed_domains = ['meituan.com']
    # start_urls = ['https://meishi.meituan.com/i/api/channel/deal/list']
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
        'Referer': 'http://meishi.meituan.com/i/?ci=20&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1',
    }

    requests_payload = {
        'app': "",
        'areaId': 0,  # 地区类型 ，默认0为附近商家
        'cateId': 1,  # 菜式类型
        'deal_attr_23': "",  # 107: "只看免预约"
        'deal_attr_24': "",  # 109: "节假日可用"
        'deal_attr_25': "",  # 115: "单人餐", 117: "双人餐", 111: "3-4人餐", 112: "5-10人餐", 110: "10人餐以上"
        'limit': 15,  # 每次获取数量
        'lineId': 0,
        'offset': 0,  # 偏移量 每次偏移15
        'optimusCode': 10,
        'originUrl': "http://meishi.meituan.com/i/?ci=20&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1",
        'partner': 126,
        'platform': 3,
        'poi_attr_20033': "",  # 20062: "买单", 20063: "在线点菜", 20064: "外卖送餐", 20065: "在线排队", 20135: "预定"
        'poi_attr_20043': "",  # 20122: "早餐" , 20123: "午餐", 20124:"下午茶", 20125: "晚餐", 20126: "夜宵"
        'riskLevel': 1,
        'sort': "default",  # "default": "智能排序", "distance": "离我最近", "avgscore": "好评优先", "solds": "人气最高",
        'stationId': 0,
        'uuid': "5548200de0ef4e8bbc3f.1543844736.2.0.0",
        'version': "8.3.3",
    }

    # def start_requests(self):
    #

    def make_requests_from_url(self, url):
        return scrapy.Request(url='https://www.baidu.com/',
                              callback=self.parse_area,
                              headers=self.headers,
                              dont_filter=True)

    def parse_area(self, response):
        url = 'https://meishi.meituan.com/i/api/channel/deal/list'
        i = 0
        for ciname in cityId[275:280]:
            # i += 1
            # if i > 2:
            #     break
            ci, cityname = ciname['id'], ciname['name']
            cookies = {'ci': ci, "cityname": cityname}
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36',
                'Referer': 'http://meishi.meituan.com/i/?ci={}&stid_b=1&cevent=imt%2Fhomepage%2Fcategory1%2F1'.format(ci),
            }
            for area in areaObj[str(ci)]:
                request_payload = copy.deepcopy(self.requests_payload)
                request_payload['areaId'] = area['id']
                yield scrapy.Request(url=url,
                                     method='POST',
                                     cookies=cookies,
                                     callback=self.parse_count,
                                     body=json.dumps(request_payload),
                                     headers=headers,
                                     meta={'requests_info': "data_totalCount",
                                           'data': request_payload,
                                           'cookies': cookies,
                                           'headers': headers},
                                     dont_filter=True)



    def parse_count(self, response):
        totalCount = json.loads(response.text)['data']['poiList']['totalCount']
        times = int(totalCount) / 15
        times = int(times) + 1 if times > int(times) else int(times)
        url = 'https://meishi.meituan.com/i/api/channel/deal/list'
        for i in range(times):
            requests_payload = response.meta['data']
            requests_payload.update({'offset': 15 * i})
            yield scrapy.Request(url=url,
                                 callback=self.parse_detail_url,
                                 method='POST',
                                 body=json.dumps(requests_payload),
                                 headers=response.meta['headers'],
                                 cookies=response.meta['cookies'],
                                 meta={"requests_info": "data_poiInfos",
                                       'headers': response.meta},
                                 dont_filter=True,
                                 )

    def parse_detail_url(self, response):
        poiInfos = json.loads(response.text)['data']['poiList']['poiInfos']
        for poiInfo in poiInfos:
            poiid = poiInfo['poiid']
            cateName = poiInfo['cateName']
            name = poiInfo['name']
            city = response.meta['headers']['cookies']['cityname']
            detail_url = 'https://meishi.meituan.com/i/poi/%s' % poiid
            yield scrapy.Request(url=detail_url,
                                 headers=response.meta['headers']['headers'],
                                 callback=self.parse_item,
                                 meta={'cateName': cateName,
                                       'name': name,
                                       'city': city,
                                       'poiid': poiid,
                                       'requests_info': 'poiInfo',
                                       'headers': response.meta['headers'],
                                       },
                                 cookies=response.meta['headers']['cookies'],
                                 dont_filter=False)

    def parse_item(self, response):
        item = MeituanMeishiItem()
        item['classify'] = response.meta['cateName']
        item['name'] = response.meta['name']
        item['city'] = response.meta['city']
        item['source'] = '美团'
        poiInfo = json.loads(re.search('"title":"商家详情","poiInfo":(.*?),"crawlerMeta"', response.text).group(1))
        item['avgPrice'] = poiInfo['avgPrice']
        item['avgScore'] = poiInfo['avgScore']
        item['address'] = poiInfo['addr']
        item['phone'] = poiInfo['phone']
        item['serviceTags'] = '支持WiFi' if poiInfo['wifi'] else "不支持WiFi"
        if poiInfo['parkingInfo']:
            item['serviceTags'] = item['serviceTags']+';停车场'
        item['openTime'] = poiInfo['openInfo']
        item['evaluateNumber'] = poiInfo['MarkNumbers']
        try:
            item['areas'] = re.search('(.*?)[区|县|市]', item['address']).group(0)
        except:
            item['areas'] = item['address']

        # data = json.loads(re.search('"crawlerMeta":(.*?)};', response.text).group(1))

        data = {
            'app': "",
            'optimusCode': 10,
            'originUrl': response.url,
            'partner': 126,
            'platform': 3,
            'poiId': response.meta['poiid'],
            'riskLevel': 1,
            'uuid': "90922a73b4274b28b6b7.1544174668.1.0.0",
            'version': "8.3.3",
        }

        headers = copy.deepcopy(response.meta['headers']['headers'])
        headers['Referer'] = response.url

        yield scrapy.Request(url='https://meishi.meituan.com/i/api/comment/tag/poi',
                             method='POST',
                             body=json.dumps(data),
                             meta={'item': item},
                             cookies=response.meta['headers']['cookies'],
                             callback=self.parse_tags,
                             headers=headers,
                             dont_filter=True)

    def parse_tags(self, response):
        item = response.meta['item']
        item['tags'] = ''
        try:
            tags = json.loads(response.text)['data']['list']
            item['tags'] = ''
            for tag in tags:
                label = tag['label']
                count = tag['count']
                label_count = '%s(%s);' % (label, count)
                item['tags'] += label_count
        except:
            pass

        yield item
