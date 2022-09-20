from flask import render_template, request, redirect
from flask_login import login_required, current_user
from flask import current_app as app
from ..db_models import *



# ------------------Filter_by_bank------------------

@app.route('/currency/get_by_bank/', strict_slashes=False)
@login_required
def get_values_by_bank():
	banks = db.session.query(Bank).filter(Bank.users.any(id=current_user.id)).all()
	return render_template('currency_templates/choose_bank.html', banks=banks)


@app.route('/currency/filter_by_bank/', methods=['POST'], strict_slashes=False)
@login_required
def filter_by_bank():
	name = request.form.get('bank')
	bank = db.session.query(Bank).filter(Bank.users.any(id=current_user.id)).filter_by(bank_name=name).first()
	currencies = bank.currencies
	values = {}

	for currency in currencies:
		value = db.session.query(Value).filter((Value.bank_id == bank.id) & 
												(Value.currency_id == currency.id)).first()
		
		buy_value = value.buy_value
		sale_value = value.sale_value
		date_of = value.date_of
		
		values[currency.currency_name] = [buy_value, sale_value, date_of]

	return render_template('currency_templates/currency_output.html', name=name, values=values)



# ------------------Filter_by_currency------------------

@app.route('/currency/get_by_currency/', strict_slashes=False)
@login_required
def get_values_by_currency():
	currencies = db.session.query(Currency).filter(Currency.users.any(id=current_user.id)).all()
	return render_template('currency_templates/choose_currency.html', currencies=currencies)


@app.route('/currency/filter_by_currency/', methods=['POST'], strict_slashes=False)
@login_required
def filter_by_currency():
	name = request.form.get('currency')
	currency = db.session.query(Currency).filter(Currency.users.any(id=current_user.id)).filter_by(currency_name=name).first()
	banks = currency.banks
	values = {}

	for bank in banks:
		value = db.session.query(Value).filter((Value.bank_id == bank.id) & 
												(Value.currency_id == currency.id)).first()

		buy_value = value.buy_value
		sale_value = value.sale_value
		date_of = value.date_of

		values[bank.bank_name] = [buy_value, sale_value, date_of]

	return render_template('currency_templates/currency_output.html', name=name, values=values)



# ------------------Filter_by_bank_and_currency------------------

@app.route('/currency/get_by_bank_and_currency/', strict_slashes=False)
@login_required
def get_values_by_bank_and_currency():
	banks = db.session.query(Bank).filter(Bank.users.any(id=current_user.id)).all()
	currencies = db.session.query(Currency).filter(Currency.users.any(id=current_user.id)).all()
	return render_template('currency_templates/choose_bank_and_currency.html', banks=banks, currencies=currencies)


@app.route('/currency/filter_by_bank_and_currency/', methods=['POST'], strict_slashes=False)
@login_required
def filter_by_bank_and_currency():
	bank_name = request.form.get('bank')
	currency_name = request.form.get('currency')

	bank = db.session.query(Bank).filter(Bank.users.any(id=current_user.id)).filter_by(bank_name=bank_name).first()
	currency = db.session.query(Currency).filter(Currency.users.any(
											id=current_user.id)).filter_by(currency_name=currency_name).first()

	values = {}

	value = db.session.query(Value).filter((Value.bank_id == bank.id) & 
										   (Value.currency_id == currency.id)).first()

	name = f'{bank.bank_name} {currency.currency_name}'

	try:
		buy_value = value.buy_value
		sale_value = value.sale_value
		date_of = value.date_of
	except:
		buy_value = 'N/A'
		sale_value = 'N/A'
		date_of = 'N/A'

	values[name] = [buy_value, sale_value, date_of]

	return render_template('currency_templates/currency_output.html', name=name, values=values)



# ------------------Deleter------------------

@app.route('/currency/delete_all_data/', strict_slashes=False)
@login_required
def currency_delete_all():
	
	db.session.query(Bank).filter(Bank.users.any(id=current_user.id)).delete(synchronize_session=False)
	db.session.query(Currency).filter(Currency.users.any(id=current_user.id)).delete(synchronize_session=False)

	db.session.commit()

	return render_template('data_deleted.html')


