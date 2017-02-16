![GSI Logo](http://vps161.cesvima.upm.es/images/stories/logos/gsi.png)
==================================

##Introduction
Footballmood is an application developed for sentiment analysis of football in Twitter based on web components and D3.js. To view your data you can use widgets and visualize it through them.

##Getting Started 
If you want to easy try Footballmood, just download this repository (cloning it to your computer or downloading it as a .zip) and open the main folder `footballmood/` in the bash console and run a simple server such as the python one `python -m SimpleHTTPServer <port>` and open the web browser with `localhost:<port>` in the url field and explore data.

To serve data for analysing, we use ElasticSearch and recover data using API REST petitions, injecting those data in widgets based on Web Components (Polymer) Technologies.

##Polymer - Web Components Technology
![Polymer logo](http://carlosortiz.co.uk/wp-content/uploads/2015/09/polymer-logo.jpg)
 
Polymer is a technology based on web components, so we could make a new component with diferent estructures of html, styles with css, and give some dinamic functions using Javascript.

Those components will be reusable only importing the tag `<component-tag></component-tag>` and they could share information using data binding among them.

##Elasticsearch
![Elastic logo](http://ecmarchitect.com/wp-content/uploads/2015/03/elastic_logo_color_horizontal.jpg)

To install elasticsearch download the latest version from https://www.elastic.co/downloads/elasticsearch


