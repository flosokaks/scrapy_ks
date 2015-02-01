"""
fetch the current website from google sites hosting
read the pages, convert to markdown

for each linked page, allow for describing the page in markdown for publishing in pelican/html.
we either want to ignore the page or parts of the page.
or we want to extract data from the site and or crawl the site.


We want to extract the information from the web pages in a readable, editable and usable format.
When we crawl the page again we want to be able to diff/merge the information from the new page with what we know about it.

For things we dont know much about, we want to run searchs for them.
"""
from scrapy import Spider, Item, Field
import html2text
import codecs
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.command import ScrapyCommand
#from scrapy import conf
from scrapy.utils.project import inside_project, get_project_settings
import scrapy.commands.runspider
import scrapy.commands
import pprint 
import scrapy.http

# AJAXCRAWL_ENABLED
# BOT_NAME
# CLOSESPIDER_ERRORCOUNT
# CLOSESPIDER_ITEMCOUNT
# CLOSESPIDER_PAGECOUNT
# CLOSESPIDER_TIMEOUT
# COMMANDS_MODULE
# COMPRESSION_ENABLED
# CONCURRENT_ITEMS
# CONCURRENT_REQUESTS
# CONCURRENT_REQUESTS_PER_DOMAIN
# CONCURRENT_REQUESTS_PER_IP
# COOKIES_DEBUG
# COOKIES_ENABLED
# DEFAULT_ITEM_CLASS
# DEFAULT_REQUEST_HEADERS
# DEPTH_LIMIT
# DEPTH_PRIORITY
# DEPTH_STATS
# DNSCACHE_ENABLED
# DOWNLOADER
# DOWNLOADER_CLIENTCONTEXTFACTORY
# DOWNLOADER_HTTPCLIENTFACTORY
# DOWNLOADER_MIDDLEWARES
# DOWNLOADER_MIDDLEWARES_BASE
# DOWNLOADER_STATS
# DOWNLOAD_DELAY
# DOWNLOAD_HANDLERS
# DOWNLOAD_HANDLERS_BASE
# DOWNLOAD_MAXSIZE
# DOWNLOAD_TIMEOUT
# DOWNLOAD_WARNSIZE
# DUPEFILTER_CLASS
# EDITOR
# EXTENSIONS
# EXTENSIONS_BASE
# FEED_EXPORTERS
# FEED_EXPORTERS_BASE
# FEED_FORMAT
# FEED_STORAGES
# FEED_STORAGES_BASE
# FEED_STORE_EMPTY
# FEED_URI
# FEED_URI_PARAMS
# HTTPCACHE_DBM_MODULE
# HTTPCACHE_DIR
# HTTPCACHE_ENABLED
# HTTPCACHE_EXPIRATION_SECS
# HTTPCACHE_IGNORE_HTTP_CODES
# HTTPCACHE_IGNORE_MISSING
# HTTPCACHE_IGNORE_SCHEMES
# HTTPCACHE_POLICY
# HTTPCACHE_STORAGE
# ITEM_PIPELINES
# ITEM_PIPELINES_BASE
# ITEM_PROCESSOR
# LOGSTATS_INTERVAL
# LOG_ENABLED
# LOG_ENCODING
# LOG_FILE
# LOG_FORMATTER
# LOG_LEVEL
# LOG_STDOUT
# LOG_UNSERIALIZABLE_REQUESTS
# MAIL_FROM
# MAIL_HOST
# MAIL_PASS
# MAIL_PORT
# MAIL_USER
# MEMDEBUG_ENABLED
# MEMDEBUG_NOTIFY
# MEMUSAGE_ENABLED
# MEMUSAGE_LIMIT_MB
# MEMUSAGE_NOTIFY_MAIL
# MEMUSAGE_REPORT
# MEMUSAGE_WARNING_MB
# METAREFRESH_ENABLED
# METAREFRESH_MAXDELAY
# NEWSPIDER_MODULE
# RANDOMIZE_DOWNLOAD_DELAY
# REDIRECT_ENABLED
# REDIRECT_MAX_TIMES
# REDIRECT_PRIORITY_ADJUST
# REFERER_ENABLED
# RETRY_ENABLED
# RETRY_HTTP_CODES
# RETRY_PRIORITY_ADJUST
# RETRY_TIMES
# ROBOTSTXT_OBEY
# SCHEDULER
# SCHEDULER_DISK_QUEUE
# SCHEDULER_MEMORY_QUEUE
# SPIDER_CONTRACTS
# SPIDER_CONTRACTS_BASE
# SPIDER_MANAGER_CLASS
# SPIDER_MIDDLEWARES
# SPIDER_MIDDLEWARES_BASE
# SPIDER_MODULES
# STATSMAILER_RCPTS
# STATS_CLASS
# STATS_DUMP
# TELNETCONSOLE_ENABLED
# TELNETCONSOLE_HOST
# TELNETCONSOLE_PORT
# TEMPLATES_DIR
# URLLENGTH_LIMIT
# USER_AGENT

class FileCache(object):
    def write(self, item, data, ext):
        title = item['response'].url
        for e in item['response'].css("h3 a::text") :
            title = e.extract()
        title = title.replace(" ","").replace("-","").replace("/","")
        fn = "pages/{0}.{1}".format(title,ext)
        o = codecs.open(fn,"w","utf-8")
        o.write(md)
        o.close()

class HtmlCache(FileCache):

    # store the website as a python object
    def process_item(self, item, spider):
        pprint.pprint(item['response'].__dict__)
        self.write(item, data, ".html")
        return item

class PythonCache(FileCache):

    # store the website as a python object
    def process_item(self, item, spider):
        data = pprint.pprint(item['response'].__dict__)
        self.write(item, data, ".py")
        return item

class MarkDownCache(FileCache):

    # convert the the html to markdown
    def process_item(self, item, spider):
        response = item['response']
        body = unicode(response.body, 'utf-8')
        data = html2text.html2text(body)
        self.write(item, data, ".md")
        return item

class Page(Item):
    response = Field()
    def __init__(self, response):
        super(Page,self).__init__()
        self['response'] = response

class OpenKansasSpider(Spider):
    name = 'openkansas'
    base = 'http://openkansas.us'
    start_urls = ['http://openkansas.us']

    def parse(self, response):
        ret = []      
        p = Page(response=response )
        ret.append(p)        
        for sel in response.xpath('//ul/li/div'):
            title = sel.xpath('a/text()').extract()
            link = sel.xpath('a/@href').extract()
            desc = sel.xpath('text()').extract()
            if link:
                l = self.base + link[0]
                #print title, l, desc
                ret.append(scrapy.http.Request(l))

        return ret

def main():
    settings = get_project_settings()
    
    settings.set('LOG_LEVEL',99)

    settings.set('ITEM_PIPELINES',{
        PythonCache : 300,
    })
    #pprint.pprint(settings.__dict__)

    cmd = scrapy.commands.runspider.Command()
    cmd.crawler_process = CrawlerProcess(settings)
    cmd.crawler_process.crawl(OpenKansasSpider)
    cmd.crawler_process.start()

main()
