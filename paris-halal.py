import scrapy

class OscarsSpider(scrapy.Spider): # on renseigne spider oú scrapper
   name = "paris-halal"
   start_urls = ['https://www.paris-halal.com/']


def parse(self, response):
    for href in response.css(r"tr[style='background:#FAEB86'] a[href*='film)']::attr(href)").extract():
         url = response.urljoin(href)
         print(url)
         req = scrapy.Request(url, callback=self.parse_titles)
         time.sleep(5)
         yield req


def parse_titles(self, response):
       for sel in response.css('html').extract():
           data = {}
           data['name'] = response.css(r"h1[id='name'] i::text").extract()
           data['tel'] = response.css(r"tr:contains('Directed by') a[href*='/paris-halal/']::text").extract()
           data['adresse'] = response.css(r"tr:contains('adresse') a[href*='/paris-halal/']::text").extract()
           data['txt'] = response.css(r"tr:contains('Description') li::text").extract()
		   data['details'] = response.css(r"tr:contains('details') li::text").extract()

       yield data