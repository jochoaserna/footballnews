# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
import random

class MarcaSpider(scrapy.Spider):
    name = "marca"     
    start_urls = [
        'http://www.marca.com/futbol/atletico.html',
        'http://www.marca.com/futbol/real-madrid.html',
        'http://www.marca.com/futbol/barcelona.html'        
    ]
    team = ""
    teamsURL = ['atletico','real-madrid', 'barcelona']
    teamsParse = ['atletico','madrid', 'barca']

    # -------------------------------------------------------------
    # ORDENES
    # $ scrapy crawl marca -o marca.json
    # -------------------------------------------------------------

    def parse(self, response):
        # follow links to each news item
        for href in response.css('h3.mod-title a::attr(href)').extract():
            yield scrapy.Request(href, callback=self.parse_news)
      
    def parse_news(self, response):
        headline = response.css('h1.js-headline.izquierda::text')[0].extract()
        articleBody = ''.join(response.css('div.row.content.cols-30-70 span.capital-letter::text ,div.row.content.cols-30-70 p::text ,div.row.content.cols-30-70 p strong::text').extract())
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
        self.team = ""
        for indexURL, elemURL in enumerate(self.teamsURL):
            if bool(re.search(elemURL, url)):
                self.team = self.teamsParse[indexURL]

        if self.team == "":
            return        
            
        item = {'@context':'http://schema.org',
            'headline':headline,
            'articleBody':articleBody,
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
            'team': self.team,
            'id':_id
            }
        yield item
        return