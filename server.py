from flask import (
	Flask,
	request,
	Response,
	render_template,
	stream_template,
	jsonify,
	abort
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

import flask_login

from markdown import markdown
import bleach

import os
import secrets


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


database = SQLAlchemy()
login_manager = flask_login.LoginManager()


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
# Posts
# --------------------------------------- #
class DatabasePost(database.Model):
	__tablename__ = 'posts'

	id: Mapped[str] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column()
	author: Mapped[str] = mapped_column()
	description: Mapped[str] = mapped_column()
	content_link: Mapped[str] = mapped_column()


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

def get_post(id: str):
	post_info = database.get_or_404(DatabasePost, id)

	with open(f'instance/posts/{post_info.content_link}', 'r') as file:
		post_content = file.read()

	post_content = markdown(post_content)
	post_content = bleach.clean(post_content, tags=allowed_clean_html_tags)

	return post_info, post_content

def render_post(id: str):
	post_info, post_content = get_post(id)

	return stream_template(
		'post.html',

		siteName = site_name,
		pageName = post_info.title,
		content = post_content
	)


# --------------------------------------- #
# Users
# --------------------------------------- #
class LoginUser(flask_login.UserMixin, database.Model):
	__tablename__ = 'users'

	id: Mapped[str] = mapped_column(primary_key=True)
	password: Mapped[str] = mapped_column()


@login_manager.user_loader
def user_loader(username):
	return database.session.get(LoginUser, username)

@login_manager.request_loader
def request_loader(request):
	username = request.form.get('username')
	return database.session.get(LoginUser, username)

@login_manager.unauthorized_handler
def unauthorized_handler():
	return abort(401)


# --------------------------------------- #
# Server
# --------------------------------------- #
def create_server():
	server = Flask(__name__, static_folder='src/static', static_url_path='/static', template_folder='src/templates')

	server.secret_key = secrets.token_hex(16)
	server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
	server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

	database.init_app(server)
	login_manager.init_app(server)


	with server.app_context():
		database.create_all()


	# --------------------------------------- #
	# API Routes
	# --------------------------------------- #
	@server.route('/api/v0/posts/create', methods=['POST'])
	@flask_login.login_required
	def route_api_create_post():
		request_json = request.get_json()

		try:
			title = request_json['title']
			description = request_json['description']
			content = request_json['content']
		except KeyError:
			return abort(400)

		author = flask_login.current_user.id

		try:
			create_post(title, author, description, content)
		except FileExistsError:
			return abort(409)

		return Response(status=200)

	@server.route('/api/v0/posts/<id>')
	def route_api_get_post(id):
		post_info, post_content = get_post(id)

		return jsonify({
			'title': post_info.title,
			'author': post_info.author,
			'description': post_info.description,
			'content': post_content
		})


	# --------------------------------------- #
	# Normal Routes
	# --------------------------------------- #
	@server.route('/')
	def route_homepage():
		return render_template('main.html', siteName=site_name, pageName='Homepage')

	@server.route('/posts/<id>')
	def route_get_post(id):
		return render_post(id)


	# --------------------------------------- #
	# API User Routes
	# --------------------------------------- #
	@server.route('/api/v0/users/login', methods=['POST'])
	def route_api_user_login():
		try:
			username = request.form['username']
			password = request.form['password']
		except KeyError:
			abort(400)

		user_info = database.get_or_404(LoginUser, username)
		if password != user_info.password:
			abort(400)

		flask_login.login_user(user_info)
		return Response(status=200)

	@server.route('/api/v0/users/logout')
	def route_api_user_logout():
		flask_login.logout_user()
		return Response(status=200)


	# --------------------------------------- #
	# Normal User Routes
	# --------------------------------------- #
	@server.route('/users/login')
	def route_user_login():
		return render_template('login.html', siteName=site_name, pageName='Login')

	@server.route('/users/logout')
	def route_user_logout():
		return render_template('logout.html', siteName=site_name, pageName='Logout')


	return server
