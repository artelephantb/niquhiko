from jinja2 import Environment, FileSystemLoader

import sqlite3

import os
from shutil import rmtree

import tomli

import minify_html


# --------------------------------------- #
# Prepare export folder
# --------------------------------------- #
try:
	rmtree('export')
except FileNotFoundError:
	pass

os.mkdir('export')


# --------------------------------------- #
# Setup
# --------------------------------------- #
with open('configuration.toml', 'rb') as file:
	site_config = tomli.load(file)

site_name = site_config['site_name']
footnote = site_config['footnote']

file_system_loader = FileSystemLoader('src/templates')
environment = Environment(loader=file_system_loader)

database = sqlite3.connect('instance/main.db')


# --------------------------------------- #
# Export: Stylesheet
# --------------------------------------- #
with open('src/static/main.css', 'r') as file:
	stylesheet = file.read()

os.mkdir('export/static')

with open('export/static/main.css', 'w') as file:
	file.write(stylesheet)

# --------------------------------------- #
# Export: homepage
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM posts')

	posts = cursor.fetchmany(3)
	posts.reverse()

template = environment.get_template('homepage.html')
output = template.render(siteName=site_name, user=False, recentPosts=posts, permissions=[], footnote=footnote)

output = minify_html.minify(output)

with open('export/index.html', 'w') as file:
	file.write(output)

# --------------------------------------- #
# Export: all posts page
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM posts')

	posts = cursor.fetchall()
	posts.reverse()

template = environment.get_template('posts.html')
output = template.render(siteName=site_name, posts=posts, user=False, permissions=[], footnote=footnote)

output = minify_html.minify(output)

os.mkdir('export/posts')

with open('export/posts/index.html', 'w') as file:
	file.write(output)
