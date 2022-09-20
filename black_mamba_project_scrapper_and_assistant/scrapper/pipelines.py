# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


from itemadapter import ItemAdapter
from datetime import datetime
from app.db_models import *
from flask import current_app as app
from app import db


# class Pipeline:

#     def __init__(self):
#         ...

#     def process_item(self, item, spider):
#         return item


class Pipeline:

    def __init__(self):
        with app.app_context():
            self.db = db


    def process_fintech(self, item, spider):

        for i in range(len(item['link'])):

            fintech_news = FintechNews()
            fintech_news.category = item['category'][i]
            fintech_news.title = item['title'][i]
            fintech_news.link = item['link'][i]
            fintech_news.published_on = item['published_on'][i]
            fintech_news.language = item['language'][0]

            exist_note = self.db.session.query(FintechNews).filter(FintechNews.users.any(
                                            id=item['user_id'][0])).filter_by(link=fintech_news.link).first()

            if exist_note:
                if exist_note.category != fintech_news.category:
                    exist_note.category = fintech_news.category
                if exist_note.title != fintech_news.title:
                    exist_note.title = fintech_news.title
                if exist_note.published_on != fintech_news.published_on:
                    exist_note.published_on = fintech_news.published_on
                if exist_note.language != fintech_news.language:
                    exist_note.language = fintech_news.language
                
                self.db.session.commit()
                fintech_news = exist_note

            else:
                try:
                    self.db.session.add(fintech_news)
                    self.db.session.commit()
                except:
                    pass

            user_fintech = self.db.session.query(UserFintech).filter(
                                                                (UserFintech.user_id == item['user_id'][0])&
                                                                (UserFintech.fintech_id == fintech_news.id)).first()

            if not user_fintech:
                user_fintech = UserFintech(user_id=item['user_id'][0], fintech_id=fintech_news.id)
                self.db.session.add(user_fintech)
                self.db.session.commit()

        return item



    def process_currency(self, item, spider):

        bank_name = item['bank_name']
        currency_name = item['currency_name']
        
        bank = self.db.session.query(Bank).filter(Bank.users.any(
                                        id=item['user_id'])).filter_by(bank_name=bank_name).first()
        if not bank:
            bank = Bank()
            bank.bank_name = bank_name
            self.db.session.add(bank)
            self.db.session.commit()
            user_bank = UserBank()
            user_bank.user_id = item['user_id']
            user_bank.bank_id = bank.id
            self.db.session.add(user_bank)
            self.db.session.commit()


        currency = self.db.session.query(Currency).filter(Currency.users.any(
                                        id=item['user_id'])).filter_by(currency_name=currency_name).first()
        if not currency:
            currency = Currency()
            currency.currency_name = currency_name
            self.db.session.add(currency)
            self.db.session.commit()
            user_currency = UserCurrency()
            user_currency.user_id = item['user_id']
            user_currency.currency_id = currency.id
            self.db.session.add(user_currency)
            self.db.session.commit()

        bank = self.db.session.query(Bank).filter(Bank.users.any(
                                        id=item['user_id'])).filter_by(bank_name=bank_name).first()
        currency = self.db.session.query(Currency).filter(Currency.users.any(
                                        id=item['user_id'])).filter_by(currency_name=currency_name).first()

        currency_bank = self.db.session.query(CurrencyBank).filter(
                                                            (CurrencyBank.currency_id == currency.id)&
                                                            (CurrencyBank.bank_id == bank.id)).first()
        
        if not currency_bank:
            currency_bank = CurrencyBank(currency_id=currency.id, bank_id=bank.id)
            self.db.session.add(currency_bank)

        value = self.db.session.query(Value).filter((Value.currency_id == currency.id)&(Value.bank_id == bank.id)).first()

        if not value:
            value = Value()
            value.bank_id = bank.id
            value.currency_id = currency.id
            self.db.session.add(value)
            
        value.buy_value = item['buy_value']
        value.sale_value = item['sale_value']
        value.date_of = datetime.now().date()

        self.db.session.commit()

        return item



    def process_item(self, item, spider):

        spider_processors = {
                             'fintech': self.process_fintech,
                             'currency': self.process_currency
                            }
        
        processor = spider_processors[spider.name]
        item = processor(item, spider)

        return item
