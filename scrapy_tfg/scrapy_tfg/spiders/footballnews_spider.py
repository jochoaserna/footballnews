# -*- coding: utf-8 -*-
import scrapy
import re
import json
import urllib.parse
import datetime
import random

class MarcaSpider(scrapy.Spider):
    name = "footballnews"     
    start_urls = [
        'http://www.marca.com/futbol/atletico.html',
        'http://www.marca.com/futbol/real-madrid.html',
        'http://www.marca.com/futbol/barcelona.html',
        'http://as.com/tag/atletico_madrid/',
        'http://as.com/tag/fc_barcelona/',
        'http://as.com/tag/real_madrid/',
        'http://www.mundodeportivo.com/futbol/atletico-madrid',
        'http://www.mundodeportivo.com/futbol/real-madrid',
        'http://www.mundodeportivo.com/futbol/fc-barcelona',
        'http://www.sport.es/es/barca/',
        'http://www.sport.es/es/real-madrid/'                    
    ]

    # -------------------------------------------------------------
    # NUEVAS ORDENES
    # $ scrapy crawl footballnews -o footballnews.json
    # -------------------------------------------------------------

    #COMENTAR!   
    # def __init__(self, team='atletico'):
    #     self.start_urls = ['http://www.marca.com/futbol/%s.html' % team]
    #COMENTAR!     

    def parse(self, response):
        # follow links to each news item
        if bool(re.search("marca.com", response.url)):
            for href in response.css('h3.mod-title a::attr(href)').extract():
                yield scrapy.Request(href, callback=self.parse_news_marca)
        elif bool(re.search("as.com", response.url)):
            for href in response.css('h2.title a::attr(href)').extract():
                yield scrapy.Request(href, callback=self.parse_news_as)
        elif bool(re.search("mundodeportivo.com/", response.url)):
            for href in response.css('h3.story-header-title a::attr(href)').extract():
                yield scrapy.Request(href, callback=self.parse_news_md)
        elif bool(re.search("sport.es", response.url)):
            for href in response.css('section.blockpad[data-section="layout-1"] h2.title a::attr(href) ,section.blockpad[data-section="layout-2"] h2.title a::attr(href)').extract():
                yield scrapy.Request(href, callback=self.parse_news_sport)
      

    def parse_news_marca(self, response):
        headline = response.css('h1.js-headline.izquierda::text')[0].extract()
        #if len(''.join(response.css('div.row.content.cols-30-70 span.capital-letter::text ,div.row.content.cols-30-70 p::text ,div.row.content.cols-30-70 p strong::text').extract())) < 3896:
        #if ''.join(response.css('div.row.content.cols-30-70 span.capital-letter::text ,div.row.content.cols-30-70 p::text ,div.row.content.cols-30-70 p strong::text').extract()) != "":
        articleBody = ''.join(response.css('div.row.content.cols-30-70 span.capital-letter::text ,div.row.content.cols-30-70 p::text ,div.row.content.cols-30-70 p strong::text').extract())
        #author = response.css('ul.author strong::text')[0].extract()
        articleSection = response.css('span.section-type::text')[0].extract()
        commentCount = response.css('li.comments-tool strong::text')[0].extract()
        datePublishedString = response.css('div.row.content.cols-30-70 time::attr(datetime)')[0].extract()
        datePublished = datetime.datetime.strptime(datePublishedString, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S+01:00')
        images = response.css('div.row.content.cols-30-70 figure img::attr(src)').extract()
        videos = response.css('div.row.content.cols-30-70 meta[itemprop="contentURL"]::attr(content)').extract()
        keywords = response.css('ul.item-tags a::text').extract()
        comments = ' - '.join(response.css('div.comentario strong.numero_comentario a::text, div.comentario p.nombre span.nombre_usuario::text, div.comentario p.nombre span.nick::text, div.comentario span.date::text, div.comentario span+p::text, div.comentario p.nombre img::attr(src)').extract())
        dateCreated = datetime.datetime.now().isoformat()
        url = response.url
        _id = str(random.randint(0,10000)) + dateCreated
        team = ""
        if bool(re.search("atletico", url)):
            team = "atletico"
        elif bool(re.search("real-madrid", url)):
            team = "madrid"
        elif bool(re.search("barcelona", url)):
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
            'videos':videos,
            'keywords':keywords,
            'comments':comments,
            'dateCreated':dateCreated,
            'newspaper': "marca",
            'url': url,
            'team': team,
            'id':_id
            }
        yield item
        return

    def parse_news_as(self, response):
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

    def parse_news_md(self, response):
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

    def parse_news_sport(self, response):
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


