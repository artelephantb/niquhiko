from jinja2 import Environment, FileSystemLoader

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


# --------------------------------------- #
# Export homepage
# --------------------------------------- #
template = environment.get_template('homepage.html')
output = template.render(siteName=site_name, user=False, recentPosts=[{'id': 'test', 'title': 'Test'}], permissions=[], footnote=footnote)

output = minify_html.minify(output)

with open('export/index.html', 'w') as file:
	file.write(output)

# --------------------------------------- #
# Export all posts page
# --------------------------------------- #
template = environment.get_template('posts.html')
output = template.render(siteName=site_name, user=False, permissions=[], footnote=footnote)

output = minify_html.minify(output)

os.mkdir('export/posts')

with open('export/posts/index.html', 'w') as file:
	file.write(output)
