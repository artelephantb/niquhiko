from flask import Flask, request, Response, send_file, render_template, render_template_string, jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

from markdown import markdown
import bleach


# Site configuration
site_name = 'Niquhiko'


allowed_clean_html_tags = ['h1', 'h2', 'h3', 'br', 'p', 'strong', 'em', 'blockquote', 'code', 'button', 'a', 'ol', 'ul', 'li', 'img', 'table', 'tr', 'td', 'tbody', 'pre']


server = Flask(__name__, static_folder='src/static', static_url_path='/static', template_folder='src/templates')
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'

database = SQLAlchemy()
database.init_app(server)


class DatabasePosts(database.Model):
	__tablename__ = 'posts'

	id: Mapped[str] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column()
	author: Mapped[str] = mapped_column()
	description: Mapped[str] = mapped_column()
	content_link: Mapped[str] = mapped_column()

with server.app_context():
	database.create_all()


@server.route('/')
def route_homepage():
	return render_template('main.html', siteName=site_name, pageName='Homepage')
