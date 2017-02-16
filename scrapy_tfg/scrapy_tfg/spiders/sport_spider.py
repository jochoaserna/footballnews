# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urllib.parse
import datetime
import random

class SportSpider(scrapy.Spider):
    name = "sport"
    start_urls = [
        'http://www.sport.es/es/barca/',
        'http://www.sport.es/es/real-madrid/'     
    ]

    # -------------------------------------------------------------
    # ORDENES
    # $ scrapy crawl sport -a team=real-madrid -o sport-rma.json
    # $ scrapy crawl sport -a team=barca -o sport-bar.json
    # -------------------------------------------------------------

    # def __init__(self, team='barca'):
    #     self.start_urls = ['http://www.sport.es/es/%s/' % team]

    def parse(self, response):
        # follow links to each news item
        for href in response.css('h2.title a::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_news)    

    def parse_news(self, response):
        headline = response.css('header.head h1::text')[0].extract()
        articleBody = ''.join(response.css('div.col-xs-12.col-sm-12.col-md-12.col-lg-12.col p::text ,div.col-xs-12.col-sm-12.col-md-12.col-lg-12.col p a::text ,div.col-xs-12.col-sm-12.col-md-12.col-lg-12.col p strong::text').extract())
        #author = response.css('div.author div.txt p::text , div.author div.txt a.author-link::text')[0].extract()
        articleSection = response.css('p.breadcrumb a::text')[0].extract()
        # commentCount = response.css('li.comments-tool strong::text')[0].extract()
        datePublishedString = response.css('div.author time::attr(datetime)')[0].extract()
        datePublished = datetime.datetime.strptime(datePublishedString, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S+01:00')
        images = response.css('div.middle figure img::attr(src)')[0].extract()
        # videos = response.css('div.row.content.cols-30-70 meta[itemprop="contentURL"]::attr(content)').extract()
        # keywords = response.css('ul.item-tags a::text').extract()
        # comments = ' - '.join(response.css('div.comentario strong.numero_comentario a::text, div.comentario p.nombre span.nombre_usuario::text, div.comentario p.nombre span.nick::text, div.comentario span.fecha::text, div.comentario span+p::text, div.comentario p.nombre img::attr(src)').extract())
        dateCreated = datetime.datetime.now().isoformat()
        url = response.url
        _id = str(random.randint(0,10000)) + dateCreated   
        team = ""
        if bool(re.search("barca", url)):
            team = "barca"
        elif bool(re.search("real-madrid", url)):
            team = "madrid"
        else:
            return          
        item = {'@context':'http://schema.org',
                'headline':headline,
                'articleBody':articleBody,
                # "author" COMMENTED BECAUSE IS MISSING IN SOME ARTICLES AND WE ARE NOT USING IT LATER
                #'author':author,
                'articleSection':articleSection,
                #'commentCount':commentCount,
                'datePublished':datePublished,
                'images':images,
                #'videos':videos,
                #'keywords':keywords,
                #'comments':comments,
                'dateCreated':dateCreated,
                'newspaper': "sport",
                'url': url,
                'team': team,
                'id':_id
                }

        yield item
        return

        