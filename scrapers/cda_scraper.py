import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

class cda(Scraper):
    """Scrapes CDA"""

    def __init__(self,database=True):
        self.database = database
        self.START_URL = "https://www.cda.nl/actueel/nieuws"
        self.BASE_URL = "https://www.cda.nl"

    def get(self):
        '''                                                                     
        Fetches articles from CDA
        '''
        self.doctype = "CDA (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=25)
        

        releases = []

        page = 0
        current_url = self.START_URL
        overview_page = requests.get(current_url)
        while overview_page.content.find(b'No results found within the selected categories and filters') == -1:
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@class="panel panel--isLink"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                current_page = requests.get(link, timeout = 10)
                tree = fromstring(current_page.text)
                try:
                    title= "".join(tree.xpath('//*[@class = "pageHeader-content"]//h1/span/text()|//*[@class ="widePhoto-content"]//h1/span/text()')).strip()
                except:
                    logger.debug("no title")
                    title = ""

                try:
                    text="".join(tree.xpath('//*[@id = "mainContent"]//div[@class = "mg-text-container"]/p/text()')).strip()
                    text=text.replace('\r', '')
                    text=text.replace('\xa0', '')
                except:
                    logger.info("no text?")
                    text =""
                try:
                    pub_date  = "".join(tree.xpath('//*[@class = "h5 paddedText-text u-background--blue u-color--white"]/text()')).strip()
                except:
                    pub_date = ""

                releases.append({'text':text,
                                 'title':title,
                                 'pub_date':pub_date,
                                 'url':link})
            page+=1
            current_url = self.START_URL+'?lookup[page-7430]='+str(page)
            overview_page=requests.get(current_url)

        return releases
			
