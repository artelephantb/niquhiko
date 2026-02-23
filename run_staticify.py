from jinja2 import Environment, FileSystemLoader

import sqlite3

from markdown import markdown
import bleach

import minify_html

import os
from shutil import rmtree, copyfile, copytree

from load_config import Config


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
config = Config()
config.load('configuration.toml')


file_system_loader = FileSystemLoader('src/templates')
environment = Environment(loader=file_system_loader)

database = sqlite3.connect('instance/main.db')


# --------------------------------------- #
# Export: Static Files
# --------------------------------------- #
copytree('src/static', 'export/static')


# --------------------------------------- #
# Export: Stylesheet
# --------------------------------------- #
template = environment.get_template('main.css')
output = template.render(colorBackground=config.site_color_background, colorBackgroundAccent=config.site_color_background_accent, colorAccent=config.site_color_accent, colorAccentHover=config.site_color_accent_hover)

with open('export/main.css', 'w') as file:
	file.write(output)

# --------------------------------------- #
# Export: Homepage
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM posts')

	posts = cursor.fetchmany(3)
	posts.reverse()

template = environment.get_template('homepage.html')
output = template.render(siteName=config.site_name, user=False, recentPosts=posts, permissions=[], footnote=config.footnote, linkBadges=config.link_badges)

output = minify_html.minify(output)

with open('export/index.html', 'w') as file:
	file.write(output)

# --------------------------------------- #
# Export: All posts page
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM posts')

	posts = cursor.fetchall()
	posts.reverse()

template = environment.get_template('posts.html')
output = template.render(siteName=config.site_name, posts=posts, user=False, permissions=[], footnote=config.footnote, linkBadges=config.link_badges)

output = minify_html.minify(output)

os.mkdir('export/posts')

with open('export/posts/index.html', 'w') as file:
	file.write(output)

# --------------------------------------- #
# Export: Post pages
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM posts')

	posts = cursor.fetchall()

template = environment.get_template('post.html')

for post_info in posts:
	with open(f'instance/posts/{post_info['content_link']}', 'r') as file:
		post_content = file.read()

	post_content = markdown(post_content)
	post_content = bleach.clean(post_content, tags=config.allowed_clean_html_tags, attributes=config.allowed_clean_html_attributes)

	output = template.render(
		id = post_info['id'],

		siteName = config.site_name,
		pageName = post_info['title'],
		content = post_content,

		like_count = post_info['like_count'],

		permissions=[],

		footnote = config.footnote,

		user = False,

		linkBadges=config.link_badges
	)

	output = minify_html.minify(output)

	os.mkdir(f'export/posts/{post_info['id']}')

	with open(f'export/posts/{post_info['id']}/index.html', 'w') as file:
		file.write(output)

# --------------------------------------- #
# Export: File Storage
# --------------------------------------- #
with database:
	database.row_factory = sqlite3.Row

	cursor = database.cursor()
	cursor.execute('SELECT * FROM file_storage')

	files = cursor.fetchall()

os.mkdir(f'export/file_storage')

for file in files:
	copyfile(f'instance/uploads/{file['content_link']}', f'export/file_storage/{file['id']}')
