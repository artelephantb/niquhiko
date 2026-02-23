from jinja2 import Environment, FileSystemLoader

import sqlite3

from markdown import markdown
import bleach

import os
from shutil import rmtree, copyfile, copytree

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

site_colors = site_config['site_colors']

site_color_background = site_colors['background']
site_color_background_accent = site_colors['background_accent']

site_color_accent = site_colors['accent']
site_color_accent_hover = site_colors['accent_hover']

allowed_clean = site_config['allowed_clean']

allowed_clean_html_tags = allowed_clean['html_tags']
allowed_clean_html_attributes = allowed_clean['html_attributes']

allowed_clean_letters = allowed_clean['letters']
allowed_clean_characters = allowed_clean['characters']

link_badges_dict = site_config['link_badges']
link_badges = []

for badge_key in link_badges_dict.keys():
	link_badges.append(link_badges_dict[badge_key])


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
output = template.render(colorBackground=site_color_background, colorBackgroundAccent=site_color_background_accent, colorAccent=site_color_accent, colorAccentHover=site_color_accent_hover)

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
output = template.render(siteName=site_name, user=False, recentPosts=posts, permissions=[], footnote=footnote, linkBadges=link_badges)

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
output = template.render(siteName=site_name, posts=posts, user=False, permissions=[], footnote=footnote, linkBadges=link_badges)

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
	post_content = bleach.clean(post_content, tags=allowed_clean_html_tags, attributes=allowed_clean_html_attributes)

	output = template.render(
		id = post_info['id'],

		siteName = site_name,
		pageName = post_info['title'],
		content = post_content,

		like_count = post_info['like_count'],

		permissions=[],

		footnote = footnote,

		user = False,

		linkBadges=link_badges
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
