# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, log
import requests
import random
import os
#import logging
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived
from twisted.internet.error import TimeoutError, ConnectError, ConnectionLost,ConnectionClosed,ConnectionRefusedError
from paperCrawl.agents import AGENTS

#logger = logging.getLogger(__name__)
class UAMiddleware(object):
    def process_request(self,request,spider):
        agent = random.choice(AGENTS)
        request.headers['User-Agent'] =agent
        #log.msg('Current UserAgent:' +agent,level=log.INFO)

class ProxyUserAgentMiddleware(object):
    DONT_RETRY_ERRORS = (
    TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ConnectionLost, ConnectionClosed, ValueError)

    def __init__(self):
        # self.ips = []
        # ip_pool = requests.get('http://119.29.150.38:8000').json()
        # for ip in ip_pool:
        #     if ip[2] == 10 :
        #         self.ips.append(ip)
        # self.ip = random.choice(self.ips)
        self.ip = ["183.169.128.30",80]

    def process_request(self,request,spider):
        #ip = random.choice(self.ips)
        agent = random.choice(AGENTS)
        format_ip = 'http://{ip}:{port}'.format(ip=self.ip[0],port=self.ip[1])
        request.meta['proxy'] = format_ip
        request.headers['User-Agent'] = agent
        #log.msg('Current UserAgent: ' + agent, level=log.INFO)
        log.msg('Current IP: ' + format_ip, level=log.INFO)

    # def process_response(self,request,response,spider):
    #     """
    #         检查response.status, 根据status是否在允许的状态码中决定是否切换到下一个proxy, 或者禁用proxy
    #     """
    #     if response.status != 200 :
    #         log.msg("ip",level=log.WARNING)
    #         new_request = request.copy()
    #         new_request.dont_filter = True
    #         return new_request
    #     else:
    #         return response

    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常
        """
        # logger.debug("%s exception: %s" % (self.proxyes[request.meta["proxy_index"]]["proxy"], exception))
        #log.msg("%s exception: %s" % (self.proxyes[request.meta["proxy_index"]]["proxy"], exception), level=log.DEBUG)
        #request_proxy_index = request.meta["proxy_index"]

        # 只有当proxy_index>fixed_proxy-1时才进行比较, 这样能保证至少本地直连是存在的.
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            # if request_proxy_index > self.fixed_proxy - 1 and self.invalid_proxy_flag:  # WARNING 直连时超时的话换个代理还是重试? 这是策略问题
            #     if self.proxyes[request_proxy_index]["count"] < self.invalid_proxy_threshold:
            #         self.invalid_proxy(request_proxy_index)
            #     elif request_proxy_index == self.proxy_index:  # 虽然超时，但是如果之前一直很好用，也不设为invalid
            #         self.inc_proxy_index()
            # else:  # 简单的切换而不禁用
            #     if request.meta["proxy_index"] == self.proxy_index:
            #         self.inc_proxy_index()
            #self.ip = random.choice(self.ips)
            self.ip = self.ip
            #agent = random.choice(AGENTS)
            format_ip = 'http://{ip}:{port}'.format(ip=self.ip[0], port=self.ip[1])
            request.meta['proxy'] = format_ip
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

class PapercrawlSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


