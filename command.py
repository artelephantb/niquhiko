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


def action_help() -> None:
	print('Actions:')
	print('=' * 100)
	for action in ACTIONS:
		print(action[0] + ':', action[1], sep='\n\t')
	print('=' * 100)

def action_start() -> None:
	try:
		environment = arguments[2]
	except IndexError:
		logger.error('Missing environment argument, try dev (for testing) or pro (for production)')

	match environment:
		case 'dev':
			runpy.run_path(os.path.join(INSTALL_PATH, 'activate_venv.py'))
			import run_debug
			run_debug.start_server()
		case _:
			logger.error(f'Invalid environment: \'{environment}\'')


match action_name:
	case 'help': action_help()
	case 'start': action_start()
	case _:
		logger.error(f'Invalid action: \'{action_name}\'')
