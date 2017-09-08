import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging
import requests

logger = logging.getLogger(__name__)

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class dailystar(rss):
    """Scrapes dailystar.co.uk"""

    def __init__(self,database=True):
        self.database=database
        self.doctype = "dailystar (www)"
        self.rss_url = "http://feeds.feedburner.com/daily-star-Latest-News"
        self.version = ".1"
        self.date    = datetime.datetime(year=2017, month=9, day=8)

    def parsehtml(self,htmlsource):
        '''
        Parses the html source to retrieve info that is not in the RSS-keys
        In particular, it extracts the following keys (which should be available in most online news:
        section    sth. like economy, sports, ...
        text        the plain text of the article
        byline      the author, e.g. "Bob Smith"
        byline_source   sth like ANP
        '''

        try:
            tree = fromstring(htmlsource)
        except:
            logger.warning("cannot parse?",type(doc),len(doc))
            logger.warning(doc)
            return("","","", "")
        try:
            title = tree.xpath("//*[@itemprop='headline']//text()")[0]
        except:
            title = ""
            logger.info("No 'title' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            teaser = tree.xpath("//*[@id='singleArticle']/header/p/text()")[0]
        except:
            teaser = ""
            logger.info("No 'teaser' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            byline = tree.xpath("//*[@class='author']//text()")[0]
        except:
            byline = ""
            logger.info("No 'byline' field encountered - don't worry, maybe it just doesn't exist.")
        try:
            text = " ".join(tree.xpath("//*[@data-type='article-body']//p/text()"))
        except:
            text = ""
            logger.info("No 'text' field encountered - don't worry, maybe it just doesn't exist.")
            
    
        extractedinfo={"title":title.strip(),
                       "teaser":teaser.strip(),
                       "byline":byline.strip(),
                       "text":text.replace("\r\n","").replace("\\","")
                      }

        return extractedinfo 