from jinja2 import Environment, FileSystemLoader

import os
from shutil import rmtree


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
file_system_loader = FileSystemLoader('src/templates')
environment = Environment(loader=file_system_loader)


# --------------------------------------- #
# Export
# --------------------------------------- #
template = environment.get_template('homepage.html')
output = template.render()

with open('export/homepage.html', 'w') as file:
	file.write(output)
