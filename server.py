from flask import Flask, request, Response, send_file, render_template, render_template_string, jsonify, abort

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

from markdown import markdown
import bleach

import os


# --------------------------------------- #
# Site Configuration
# --------------------------------------- #
site_name = 'Niquhiko'

allowed_clean_html_tags = ['h1', 'h2', 'h3', 'br', 'p', 'strong', 'em', 'blockquote', 'code', 'button', 'a', 'ol', 'ul', 'li', 'img', 'table', 'tr', 'td', 'tbody', 'pre']

allowed_clean_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
allowed_clean_characters = allowed_clean_letters + '!?$%*&~`():\'"/'


# --------------------------------------- #
# Setup
# --------------------------------------- #
os.makedirs('instance/posts', exist_ok=True)


server = Flask(__name__, static_folder='src/static', static_url_path='/static', template_folder='src/templates')
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'

database = SQLAlchemy()
database.init_app(server)


class DatabasePost(database.Model):
	__tablename__ = 'posts'

	id: Mapped[str] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column()
	author: Mapped[str] = mapped_column()
	description: Mapped[str] = mapped_column()
	content_link: Mapped[str] = mapped_column()

with server.app_context():
	database.create_all()


def create_post(title: str, author: str, description: str, content: str):
	id = get_cleaned_string(title, allowed_characters=allowed_clean_letters, separator='-', all_lower=True)

	with open(f'instance/posts/{id}', 'x') as file:
		file.write(content)

	post = DatabasePost(
		id = id,
		title = get_cleaned_string(title),
		author = get_cleaned_string(author),
		description = get_cleaned_string(description),
		content_link = id
	)

	database.session.add(post)
	database.session.commit()


# --------------------------------------- #
# Sanatizers
# --------------------------------------- #
def get_cleaned_string(name: str, allowed_characters=allowed_clean_characters, separator=' ', all_lower=False):
	if all_lower:
		name = name.lower()
	name = name.replace('  ', '')

	final = ''

	for letter in name:
		if letter in allowed_characters:
			final += letter
		elif letter == ' ':
			final += separator

	return final


# --------------------------------------- #
# API Routes
# --------------------------------------- #
@server.route('/api/v0/posts/create', methods=['POST'])
def route_create_post():
	request_json = request.get_json()

	try:
		title = request_json['title']
		author = request_json['author']
		description = request_json['description']
		content = request_json['content']
	except KeyError:
		return abort(400)

	try:
		create_post(title, author, description, content)
	except FileExistsError:
		return abort(409)

	return Response(status=200)


# --------------------------------------- #
# Normal Routes
# --------------------------------------- #
@server.route('/')
def route_homepage():
	return render_template('main.html', siteName=site_name, pageName='Homepage')
