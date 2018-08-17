# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider,Request
import json
from zhihuuser.items import UserItem

class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com']

    start_user = 'excited-vczh'
    #用户
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    uesr_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'
    #关注列表
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include{include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    #粉丝列表
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include{include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answere'

    #当spider启动爬取时调用
    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user,include=self.uesr_query),self.parse_user)
        yield Request(self.follows_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),\
                      callback=self.parse_follows)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),\
                      callback=self.parse_followers)
    #解析单个用户的信息
    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
       # item.fields输出items.py里面定义的所有名称
        for field in item.fields:
            if field in result.keys():
                #字典的get函数拿到值
                item[field] = result.get(field)
        yield item
        #每一个人再请求自己的关注列表
        yield Request(self.follows_url.format(user=result.get('url_token'),include=self.follows_query,limit=20,offset=0),\
                      callback=self.parse_follows)
        #请求粉丝列表
        yield Request(self.followers_url.format(user=result.get('url_token'), include=self.followers_query, limit=20, offset=0), \
            callback=self.parse_followers)

    #解析关注列表的信息
    def parse_follows(self,response):
        results = json.loads(response.text)
        #得到关注列表信息，利用parse_user解析每个关注人的信息
        if 'data' in results.keys():
            #分析网页后，用户关注列表data的值是一个列表
            for result in results.get('data'):
                #print('我在解析',result.get('url_token'))
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.uesr_query),callback=self.parse_user)

        #分页判断
        if 'paging' in results.keys() and ( results.get('paging').get('is_end') == False):
            next_page = results.get('paging').get('next')
            #print('开始请求下一页',next_page)
            yield Request(url=next_page,callback=self.parse_follows)

 # 解析粉丝列表的信息
    def parse_followers(self, response):
        results = json.loads(response.text)
        # 得到关注列表信息，利用parse_user解析每个关注人的信息
        if 'data' in results.keys():
            # 分析网页后，用户关注列表data的值是一个列表
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.uesr_query),
                                callback=self.parse_user)

        # 分页判断
        if 'paging' in results.keys() and (results.get('paging').get('is_end') == False):
            next_page = results.get('paging').get('next')
            yield Request(url=next_page, callback=self.parse_followers)




