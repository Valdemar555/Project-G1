from flask import render_template, request, redirect
from flask_login import login_required, current_user
from sqlalchemy import desc
from config import FINTECH_MAX_PAGES, FINTECH_LANGS
from flask import current_app as app
from ..db_models import *


# ------------------Getter------------------

@app.route('/fintech/get_all_data/', strict_slashes=False)
@login_required
def get_all_headers():
	headers = db.session.query(FintechNews).filter(FintechNews.users.any(id=current_user.id)).all()
	return render_template('fintech_templates/fintech_output.html', headers=headers)


# ------------------Subject_filter------------------

@app.route('/fintech/choose_subject/', strict_slashes=False)
@login_required
def choose_subject():
	subjects = set([item[0] for item in db.session.query(FintechNews.category)])
	return render_template('fintech_templates/choose_subject.html', subjects=subjects)


@app.route('/fintech/sort_by_subject/', methods=['POST'], strict_slashes=False)
@login_required
def sort_by_subject():
	subject = request.form.get('subject')
	headers = db.session.query(FintechNews).filter(FintechNews.users.any(id=current_user.id)).filter_by(category=subject).all()
	return render_template('fintech_templates/fintech_output.html', headers=headers)


# ------------------Language_filter------------------

@app.route('/fintech/choose_language/', strict_slashes=False)
@login_required
def choose_language():
	langs = FINTECH_LANGS
	return render_template('fintech_templates/choose_language.html', langs=langs)


@app.route('/fintech/sort_by_language/', methods=['POST'], strict_slashes=False)
@login_required
def sort_by_language():
	lang = request.form.get('lang')
	headers = db.session.query(FintechNews).filter(FintechNews.users.any(
								id=current_user.id)).filter_by(language=lang).order_by(desc(FintechNews.published_on)).all()

	return render_template('fintech_templates/fintech_output.html', headers=headers)


# ------------------By_date_sorter------------------

@app.route('/fintech/order_by_date/', strict_slashes=False)
@login_required
def order_by_date():
	headers = db.session.query(FintechNews).filter(FintechNews.users.any(
								id=current_user.id)).order_by(desc(FintechNews.published_on)).all()

	return render_template('fintech_templates/fintech_output.html', headers=headers)


# ------------------Updater------------------

@app.route('/fintech/update_parameters/', strict_slashes=False)
@login_required
def update_parameters():
	max_pages = FINTECH_MAX_PAGES
	langs = FINTECH_LANGS
	return render_template('fintech_templates/fintech_update.html', max_pages=max_pages, langs=langs)


# ------------------Deleter------------------

@app.route('/fintech/delete_all_data/', strict_slashes=False)
@login_required
def fintech_delete_all():
	db.session.query(FintechNews).filter(FintechNews.users.any(id=current_user.id)).delete(synchronize_session=False)
	db.session.commit()

	return render_template('data_deleted.html')
