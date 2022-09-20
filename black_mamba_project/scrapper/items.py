# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


from scrapy.item import Item, Field
from datetime import datetime
from scrapy.loader.processors import MapCompose

from config import FINTECH_START_URLS


# FINTECH
def create_fintech_link(text):
    base_url = FINTECH_START_URLS[0]
    return f'{base_url}{text}'

def create_fintech_date(text):
    text = text.split('|')[0].strip()
    return datetime.strptime(text, '%d.%m.%Y').date()


class FintechItem(Item):

    category = Field()
    title = Field()
    link = Field(input_processor=MapCompose(create_fintech_link))
    published_on = Field(input_processor=MapCompose(create_fintech_date))
    language = Field()
    user_id = Field()



# CURRENCY
class CurrencyItem(Item):

    bank_name = Field()
    currency_name = Field()
    buy_value = Field()
    sale_value = Field()
    user_id = Field()


