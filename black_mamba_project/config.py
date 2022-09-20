
# SCRAPPER_PARAMS
FINTECH_START_URLS = ['https://www.stockworld.com.ua']
FINTECH_MAX_PAGES = 35
FINTECH_LANGS = ['ru', 'en']

CURRENCY_START_URLS = ['https://minfin.com.ua/currency/banks/']
CURRENCY_BASE_URL = 'https://minfin.com.ua'


class Config:
	
	# DATABASE
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost/news_scrapper'
	SQLALCHEMY_ECHO = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# AUTHENTICATION
	SECRET_KEY = '9OLWxND4o83j4K4iuopO'
