import os
import subprocess

from datetime import datetime

from zipfile import ZipFile


BRANCH = 'main'
ARCHIVE_URL = f'https://github.com/artelephantb/niquhiko/archive/refs/heads/{BRANCH}.zip'

USER_HOME_PATH = os.path.expanduser('~')
INSTALL_PATH = os.path.join(USER_HOME_PATH, '.niquhiko')

COMMAND_PATH = '/usr/local/bin/nqh'


try:
	os.mkdir(INSTALL_PATH)
except FileExistsError:
	print('\033[91mERROR: Niquhiko already installed\033[0m')
	exit(1)

now = datetime.now()
random_download_name = 'Download' + str(int(now.timestamp()))

subprocess.run(['wget', '-O', random_download_name, ARCHIVE_URL])


with ZipFile(random_download_name) as opened_zip:
	names = opened_zip.namelist()
	main_folder = names[0]
	del names[0]

	for name in names:
		new_name = name.removeprefix(main_folder)
		path = os.path.join(INSTALL_PATH, new_name)

		zip_info = opened_zip.getinfo(name)

		if zip_info.is_dir():
			os.mkdir(path)
			continue

		with opened_zip.open(name) as read_file:
			with open(path, 'wb') as write_file:
				write_file.write(read_file.read())

os.remove(random_download_name)


abs_script_path = os.path.abspath(os.path.join(INSTALL_PATH, 'command.py'))

subprocess.run(['chmod', '+x', abs_script_path])
subprocess.run(['sudo', 'ln', '-s', abs_script_path, COMMAND_PATH])
