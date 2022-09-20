import scrapy
from scrapper.items import CurrencyItem
from datetime import datetime

from config import CURRENCY_START_URLS, CURRENCY_BASE_URL


class Currency(scrapy.Spider):

	name = 'currency'

	def __init__(self, category, *args, **kwargs):
		super(Currency, self).__init__(*args, **kwargs)
		
		self.user_id = category
		self.start_urls = CURRENCY_START_URLS
		self.base_url = CURRENCY_BASE_URL

	def parse(self, response):

		links_main_currencies = response.css('div.mfm-tab-menu a::attr(href)').getall()[:-1]
		links_other_currencies = response.css('div.mfm-tab-menu div.mfSelect-list-item::attr(data-href)').getall()
		links_main_currencies.extend(links_other_currencies)
		links_all_currencies = list(set(links_main_currencies))

		date = datetime.now().date().strftime('%Y-%m-%d')

		for link in links_all_currencies:
			url = f'{self.base_url}{link}{date}/'
			yield response.follow(url, callback=self.parse_titles)


	def parse_titles(self, response):

		banks = response.css('div.mfm-grey-bg tr.row--collapse')
		currency_name = response.css('div.mfm-tab-menu a.active::text').get()

		item = CurrencyItem()

		for bank in banks:
			bank_name = bank.css('a::text').get()
			buy_value = bank.css('td.responsive-hide.mfm-text-right.mfm-pr0::text').get()
			sale_value = bank.css('td.responsive-hide.mfm-text-left.mfm-pl0::text').get()		

			try:
				item['bank_name'] = bank_name.split('\n')[0]
				item['currency_name'] = currency_name.replace('\n','').lower()
				item['buy_value'] = float(buy_value)
				item['sale_value'] = float(sale_value)
				item['user_id'] = self.user_id
			except:
				continue

			yield item



# https://minfin.com.ua/currency/banks/eur/2022-09-18/

# response.css('div.mfm-tab-menu a::attr(href)').getall()[:-1] - links to main currencies
# response.css('div.mfm-tab-menu div.mfSelect-list-item::attr(data-href)').getall() - links to other currencies

# response.css('div.mfm-tab-menu a::text').getall()[:-2] - names of main currencies
# response.css('div.mfm-tab-menu div.mfSelect-list-item span.mfSelect-col2::text').getall() - names of other currencies

# response.css('div.mfm-tab-menu a.active::text').get().replace('\n','') - get actual currency name

# response.css('div.mfm-grey-bg tr.row--collapse a::text').getall()  + split('\n')[0] - names of banks
# response.css('div.mfm-grey-bg tr.row--collapse td.js-ex-rates.mfcur-table-bankname::attr(data-title)').getall() - buy/sale

