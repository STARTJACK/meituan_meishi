import base64
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
# 代理服务器
proxyServer = "http://http-dyn.abuyun.com:9020"

# 代理隧道验证信息
proxyUser = "H9W85482747Y4Q8D"
proxyPass = "DB543A4DBAEFB1F8"

proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth


from fake_useragent import UserAgent


class UserAgentMiddleware(object):
    def __init__(self, crawler):
        self.ua = UserAgent()
        self.ua_type = 'random'  # 从setting文件中读取RANDOM_UA_TYPE值

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):  ###系统电泳函数
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User_Agent', get_ua())



import logging
logger = logging.getLogger("retry")
class MyRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response

        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        if b'verify' in response.body[15:30]:
            reason = "需要验证"
            return self._retry(request, reason, spider) or response

        if "data_totalCount" in request.meta.values():
            if b'totalCount' not in response.body[30:44]:
                reason = 'data_totalCount访问错误'
                return self._retry(request, reason, spider) or response

        if "data_poiInfos" in request.meta.values():
            if b'data' not in response.body[10:20]:
                reason = 'data_poiInfos访问错误'
                return self._retry(request, reason, spider) or response
        if "poiInfo" in request.meta.values():
            if b'poiInfo' not in response.body:
                reason = 'poiInfo访问错误'
                return self._retry(request, reason, spider) or response

        return response

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        retry_times = 10

        if 'max_retry_times' in request.meta:
            retry_times = request.meta['max_retry_times']

        stats = spider.crawler.stats
        if retries <= retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust

            if isinstance(reason, Exception):
                reason = global_object_name(reason.__class__)

            stats.inc_value('retry/count')
            stats.inc_value('retry/reason_count/%s' % reason)
            return retryreq
        else:
            stats.inc_value('retry/max_reached')
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})


from selenium import webdriver
import time
class MyRedirectMiddleware(RedirectMiddleware):

    def process_response(self, request, response, spider):
        if (request.meta.get('dont_redirect', False) or
                response.status in getattr(spider, 'handle_httpstatus_list', []) or
                response.status in request.meta.get('handle_httpstatus_list', []) or
                request.meta.get('handle_httpstatus_all', False)):
            return response

        allowed_status = (301, 302, 303, 307, 308)
        if 'Location' not in response.headers or response.status not in allowed_status:
            return response
        else:
            browser = webdriver.Chrome(executable_path=r'C:\Users\STARTJACK\AppData\Local\Google\Chrome\Application\chromedriver.exe')
            url = response.url
            time.sleep(10)
            browser.get(url)
            return response

