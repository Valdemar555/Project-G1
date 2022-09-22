import scrapy
from scrapper.items import FintechItem
from scrapy.loader import ItemLoader

from config import FINTECH_START_URLS

class Fintech(scrapy.Spider):

	name = 'fintech'

	def __init__(self, category, *args, **kwargs):
		super(Fintech, self).__init__(*args, **kwargs)

		self.max_page = int(category[0])
		self.lang = category[1]
		self.user_id = category[2]
		self.start_urls = FINTECH_START_URLS
		self.base_url = self.start_urls[0]
	

	def parse(self, response):

		for i in range(1, self.max_page + 1):
			url = f'{self.base_url}/{self.lang}/{i}'
			yield response.follow(url, callback=self.parse_titles)


	def parse_titles(self, response):

		titles = response.css('div.info-title::text').getall()
		categories = response.css('span.info-c::text').getall()
		links = response.css('a.info._1x._n::attr(href)').getall()
		dates = response.css('div.info-h div.info-time::text').getall()

		loader = ItemLoader(item=FintechItem(), response=response)

		loader.add_value('category', categories)
		loader.add_value('title', titles)
		loader.add_value('link', links)
		loader.add_value('published_on', dates)
		loader.add_value('language', self.lang)
		loader.add_value('user_id', self.user_id)

		yield loader.load_item()
