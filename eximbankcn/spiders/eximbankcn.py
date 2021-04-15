import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from eximbankcn.items import Article


class eximbankcnSpider(scrapy.Spider):
    name = 'eximbankcn'
    start_urls = ['http://www.eximbank.gov.cn/info/szyw/index.html']
    page = 0

    def parse(self, response):
        links = response.xpath('//ul[@class="listDetails"]/li/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'http://www.eximbank.gov.cn/info/szyw/index_{self.page}.html'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3[@class="noticeDetTitle"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h4[@class="noticeDetDate"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="TRS_Editor"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
