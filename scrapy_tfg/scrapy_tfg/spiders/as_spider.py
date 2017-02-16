# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urllib.parse
import datetime
import random

class AsSpider(scrapy.Spider):
    name = "as"
    start_urls = [
        'http://as.com/tag/atletico_madrid/',
        'http://as.com/tag/fc_barcelona/',
        'http://as.com/tag/real_madrid/'        
    ]

    # -------------------------------------------------------------
    # ORDENES
    # $ scrapy crawl as -a team=atletico_madrid -o as-atm.json
    # $ scrapy crawl as -a team=real_madrid -o as-rma.json
    # $ scrapy crawl as -a team=fc_barcelona -o as-bar.json
    # -------------------------------------------------------------

    # def __init__(self, team='atletico_madrid'):
    #     self.start_urls = ['http://as.com/tag/%s/' % team]

    def parse(self, response):
        # follow links to each news item
        for href in response.css('h2.title a::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_news)
    
    def parse_news(self, response):
        headline = response.css('h1.titular-articulo::text')[0].extract()
        #if len(''.join(response.css('div.int-articulo p:not(.txt-art-tags):not(.tit-detalle):not(.fecha-detalle)::text, div.int-articulo p a em::text, div.int-articulo p strong a::text, div.int-articulo p a::text, div.int-articulo p strong::text, div.int-articulo p span::text').extract())) < 3896:
        articleBody = ''.join(response.css('div.int-articulo p:not(.txt-art-tags):not(.tit-detalle):not(.fecha-detalle)::text, div.int-articulo p a em::text, div.int-articulo p strong a::text, div.int-articulo p a::text, div.int-articulo p strong::text, div.int-articulo p span::text').extract())
        ##author = response.css('a.author-pic span::text')[0].extract()
        articleSection = response.css('p.subtit-art a::text')[0].extract()
        commentCount = response.css('div.contador span::text')[0].extract() #DUDA
        datePublished = response.css('div.art-info time::attr(datetime)')[0].extract()
        images = response.css('div.cont-img-dest-art img::attr(src), div.int-articulo p+figure img::attr(src)').extract()
        #videos = response.css('div.row.content.cols-30-70 meta[itemprop="contentURL"]::attr(content)').extract()
        keywords = response.css('div.cont-art-tags li a::text').extract()
        #comments = ' - '.join(response.css('div.comentario strong.numero_comentario a::text, div.comentario p.nombre span.nombre_usuario::text, div.comentario p.nombre span.nick::text, div.comentario span.fecha::text, div.comentario span+p::text, div.comentario p.nombre img::attr(src)').extract())
        dateCreated = datetime.datetime.now().isoformat()
        url = response.url
        _id = str(random.randint(0,10000)) + dateCreated
        team = ""
        if bool(re.search("ATLÉTICO", articleSection)):
            team = "atletico"
        elif bool(re.search("REAL MADRID", articleSection)):
            team = "madrid"
        elif bool(re.search("BARCELONA", articleSection)):
            team = "barca"
        else:
            return  
        item = {'@context':'http://schema.org',
                'headline':headline,
                'articleBody':articleBody,
                # "author" COMMENTED BECAUSE IS MISSING IN SOME ARTICLES AND WE ARE NOT USING IT LATER
                #'author':author,
                'articleSection':articleSection,
                'commentCount':commentCount,
                'datePublished':datePublished,
                'images':images,
                #'videos':videos,
                'keywords':keywords,
                #'comments':comments,
                'dateCreated':dateCreated,
                'newspaper': "as",
                'url': url,
                'team': team,
                'id':_id
                    }
        yield item
        return