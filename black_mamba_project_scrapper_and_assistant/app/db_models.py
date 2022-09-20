from flask_login import UserMixin
from . import db


# DB_FOR_USERS
class User(UserMixin, db.Model):

	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(256), unique=True)
	email = db.Column(db.String(256), unique=True)
	password = db.Column(db.String(128))
	fintech = db.relationship('FintechNews', secondary='user_fintech', back_populates='users')
	banks = db.relationship('Bank', secondary='user_bank', back_populates='users')
	currencies = db.relationship('Currency', secondary='user_currency', back_populates='users')



# FINTECH_NEWS
class UserFintech(db.Model):

	__tablename__ = 'user_fintech'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
	fintech_id = db.Column(db.Integer, db.ForeignKey('fintech_news.id', ondelete='CASCADE'))


class FintechNews(db.Model):

	__tablename__ = 'fintech_news'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	category = db.Column(db.String(128), nullable=True)
	title = db.Column(db.String(128), nullable=False)
	link = db.Column(db.String(512), nullable=False)
	published_on = db.Column(db.Date, nullable=True)
	language = db.Column(db.String(8), nullable=False)
	users = db.relationship('User', secondary='user_fintech', back_populates='fintech', cascade='all, delete')



# CURRENCY_IN_DIFFERENT_BANKS
class CurrencyBank(db.Model):

	__tablename__ = 'currency_bank'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	currency_id = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='CASCADE'))
	bank_id = db.Column(db.Integer, db.ForeignKey('bank.id', ondelete='CASCADE'))


class UserBank(db.Model):

	__tablename__ = 'user_bank'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	bank_id = db.Column(db.Integer, db.ForeignKey('bank.id', ondelete='CASCADE'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class UserCurrency(db.Model):

	__tablename__ = 'user_currency'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	currency_id = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='CASCADE'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))


class Bank(db.Model):

	__tablename__ = 'bank'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	bank_name = db.Column(db.String(128), nullable=False)
	currencies = db.relationship('Currency', secondary='currency_bank', back_populates='banks')
	values = db.relationship('Value', back_populates='bank')
	users = db.relationship('User', secondary='user_bank', back_populates='banks', cascade='all, delete')


class Currency(db.Model):

	__tablename__ = 'currency'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	currency_name = db.Column(db.String(128), nullable=False)
	banks = db.relationship('Bank', secondary='currency_bank', back_populates='currencies')
	values = db.relationship('Value', back_populates='currency')
	users = db.relationship('User', secondary='user_currency', back_populates='currencies', cascade='all, delete')
	

class Value(db.Model):

	__tablename__ = 'value'

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	bank_id = db.Column(db.Integer, db.ForeignKey('bank.id', ondelete='CASCADE'))
	bank = db.relationship('Bank', back_populates='values', cascade='all, delete')
	currency_id = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='CASCADE'))
	currency = db.relationship('Currency', back_populates='values', cascade='all, delete')
	buy_value = db.Column(db.Float, nullable=False)
	sale_value = db.Column(db.Float, nullable=False)
	date_of = db.Column(db.Date, nullable=False)


# class SaleValues(db.Model):

# 	__tablename__ = 'sale_values'

# 	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
# 	bank_id = db.Column(db.Integer, db.ForeignKey('bank.id', ondelete='CASCADE'))
# 	bank = db.relationship('Bank', back_populates='sale_values')
# 	currency_id = db.Column(db.Integer, db.ForeignKey('currency.id', ondelete='CASCADE'))
# 	currency = db.relationship('Currency', back_populates='sale_values')
# 	sale_value = db.Column(db.Float, nullable=False)
# 	date_of = db.Column(db.Date, nullable=False)
