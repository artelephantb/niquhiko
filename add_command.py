import logger

import os
import subprocess


BIN_PATH = '/usr/local/bin/nqh'


if os.path.isfile(BIN_PATH):
	logger.error('Niquhiko command already added')

abs_script_path = os.path.abspath('./command.py')

subprocess.run(['chmod', '+x', abs_script_path])
subprocess.run(['sudo', 'ln', '-s', abs_script_path, BIN_PATH])
