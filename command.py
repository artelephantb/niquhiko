#!/usr/bin/env python3

import os
import sys
import logger

import runpy


USER_HOME_PATH = os.path.expanduser('~')
INSTALL_PATH = os.path.join(USER_HOME_PATH, '.niquhiko')

ACTIONS = [
	[
		'help',
		'Shows a list of all actions'
	],
	[
		'new',
		'Creates a new project, usage: nqh new <location> <name>'
	],
	[
		'start',
		'Starts the server in either dev (for testing) or pro (for production)'
	]
]

arguments = sys.argv

file_name = arguments[0]
try:
	action_name = arguments[1]
except IndexError:
	logger.error('Missing action, try \'help\'')

current_working_directory = os.getcwd()
os.chdir(INSTALL_PATH)


runpy.run_path(os.path.join(INSTALL_PATH, 'activate_venv.py'))

import tomli_w


def action_help() -> None:
	print('Actions:')
	print('=' * 100)
	for action in ACTIONS:
		print(action[0] + ':', action[1], sep='\n\t')
	print('=' * 100)

def action_new() -> None:
	try:
		project_location = arguments[2]
	except IndexError:
		logger.error('Missing project location')
	try:
		project_name = arguments[3]
	except IndexError:
		logger.error('Missing project name')

	real_project_location = os.path.join(current_working_directory, project_location)

	project_file = {
		'project': {
			'name': project_name,
			'type': 'blog_site'
		}
	}

	os.makedirs(real_project_location)
	with open(os.path.join(real_project_location, 'project.toml'), 'wb') as file:
		tomli_w.dump(project_file, file)

def action_start() -> None:
	try:
		environment = arguments[2]
	except IndexError:
		logger.error('Missing environment argument, try dev (for testing) or pro (for production)')

	from server import create_server

	match environment:
		case 'dev':
			created_server = create_server(current_working_directory)
			created_server.run(port=8000)
		case _:
			logger.error(f'Invalid environment: \'{environment}\'')


match action_name:
	case 'help': action_help()
	case 'new': action_new()
	case 'start': action_start()
	case _:
		logger.error(f'Invalid action: \'{action_name}\'')
