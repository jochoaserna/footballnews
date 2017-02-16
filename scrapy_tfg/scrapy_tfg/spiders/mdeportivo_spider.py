# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urllib.parse
import datetime
import random

class MundodeportivoSpider(scrapy.Spider):
    name = "md"
    start_urls = [
        'http://www.mundodeportivo.com/futbol/atletico-madrid',
        'http://www.mundodeportivo.com/futbol/real-madrid',
        'http://www.mundodeportivo.com/futbol/fc-barcelona'        
    ]

    # -------------------------------------------------------------
    # ORDENES
    # $ scrapy crawl md -a team=atletico-madrid -o md-atm.json
    # $ scrapy crawl md -a team=real-madrid -o md-rma.json
    # $ scrapy crawl md -a team=fc-barcelona -o md-bar.json
    # -------------------------------------------------------------

    # def __init__(self, team='atletico_madrid'):
    #     self.start_urls = ['http://www.mundodeportivo.com/futbol/%s' % team]

    def parse(self, response):
        # follow links to each news item
        for href in response.css('h3.story-header-title a::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_news)    

    def parse_news(self, response):
        headline = response.css('h1.story-leaf-title::text')[0].extract()
        articleBody = ''.join(response.css('div.story-leaf-txt-p p::text ,div.story-leaf-txt-p p b::text ,div.story-leaf-txt-p p a::text').extract())
        #author = response.css('div.story-leaf-author-text span::text')[0].extract()
        #articleSection = response.css('span.section-type::text')[0].extract()
        #commentCount = response.css('div.fyre-comment-count span::text')[0].extract()
        datePublished = response.css('div.story-leaf-body.story-leaf-indent time::attr(datetime)')[0].extract()
        images = response.css('div.container figure img::attr(src)')[1].extract()
        videos = response.css('div.html-box-center iframe::attr(src)').extract()
        keywords = response.css('li.story-leaf-topics-item a::text').extract()
        #comments = ' - '.join(response.css('div.comentario strong.numero_comentario a::text, div.comentario p.nombre span.nombre_usuario::text, div.comentario p.nombre span.nick::text, div.comentario span.fecha::text, div.comentario span+p::text, div.comentario p.nombre img::attr(src)').extract())
        dateCreated = datetime.datetime.now().isoformat()
        url = response.url
        _id = str(random.randint(0,10000)) + dateCreated
        team = ""
        if bool(re.search("atletico-madrid", url)):
            team = "atletico"
        elif bool(re.search("real-madrid", url)):
            team = "madrid"
        elif bool(re.search("fc-barcelona", url)):
            team = "barca"
        else:
          return            
        item = {'@context':'http://schema.org',
                'headline':headline,
                'articleBody':articleBody,
                # "author" COMMENTED BECAUSE IS MISSING IN SOME ARTICLES AND WE ARE NOT USING IT LATER
                #'author':author,
                #'articleSection':articleSection,
                #'commentCount':commentCount,
                'datePublished':datePublished,
                'images':images,
                'videos':videos,
                'keywords':keywords,
                #'comments':comments,
                'dateCreated':dateCreated,
                'newspaper': "md",
                'url': url,
                'team': team,
                'id':_id
                }

        yield item
        return

        