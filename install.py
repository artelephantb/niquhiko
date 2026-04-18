import os
import os.path
import sys

import subprocess
from subprocess import Popen, PIPE

from threading import Thread

from urllib.parse import urlparse
from urllib.request import urlretrieve

import venv

from datetime import datetime

from zipfile import ZipFile


BRANCH = 'main'
ARCHIVE_URL = f'https://github.com/artelephantb/niquhiko/archive/refs/heads/{BRANCH}.zip'

USER_HOME_PATH = os.path.expanduser('~')
INSTALL_PATH = os.path.join(USER_HOME_PATH, '.niquhiko')

COMMAND_PATH = '/usr/local/bin/nqh'

PYPI_BASE_PROJECT_URL = 'https://pypi.org/project/'


class VenvInstaller(venv.EnvBuilder):
	# Copyright (C) 2013 Vinay Sajip
	#
	# Redistribution and use in source and binary forms, with or without
	# modification, are permitted provided that the following conditions are
	# met:
	#
	# 1.  Redistributions of source code must retain the above copyright
	#     notice, this list of conditions and the following disclaimer.
	#
	# 2.  Redistributions in binary form must reproduce the above copyright
	#     notice, this list of conditions and the following disclaimer in the
	#     documentation and/or other materials provided with the distribution.
	#
	# 3.  Neither the name of the copyright holder nor the names of its
	#     contributors may be used to endorse or promote products derived from
	#     this software without specific prior written permission.
	#
	# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
	# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
	# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
	# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
	# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
	# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
	# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
	# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
	# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
	# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

	"""
	A builder that installs packages from URLs

	This builder installs setuptools and pip so that you can pip or
	easy_install other packages into the created environment.

	:param nodist: If True, setuptools and pip are not installed into the
				created environment.
	:param nopip: If True, pip is not installed into the created
				environment.
	:param progress: If setuptools or pip are installed, the progress of the
					installation can be monitored by passing a progress
					callable. If specified, it is called with two
					arguments: a string indicating some progress, and a
					context indicating where the string is coming from.
					The context argument can have one of three values:
					'main', indicating that it is called from virtualize()
					itself, and 'stdout' and 'stderr', which are obtained
					by reading lines from the output streams of a subprocess
					which is used to install the app.

					If a callable is not specified, default progress
					information is output to sys.stderr.
	"""

	def __init__(self, *args, **kwargs):
		self.nopip = kwargs.pop('nopip', False)
		self.progress = kwargs.pop('progress', None)
		self.verbose = kwargs.pop('verbose', False)

		self.scripts_to_install = []

		super().__init__(*args, **kwargs)

	def post_setup(self, context):
		"""
		Set up any packages which need to be pre-installed into the
		environment being created.

		:param context: The information for the environment creation request
						being processed.
		"""
		os.environ['VIRTUAL_ENV'] = context.env_dir

		for script in self.scripts_to_install:
			self.install_script(context, script[0], script[1])

	def reader(self, stream, context):
		"""
		Read lines from a subprocess' output stream and either pass to a progress
		callable (if specified) or write progress information to sys.stderr.
		"""
		progress = self.progress
		while True:
			s = stream.readline()
			if not s:
				break
			if progress is not None:
				progress(s, context)
			else:
				if not self.verbose:
					sys.stderr.write('.')
				else:
					sys.stderr.write(s.decode('utf-8'))
				sys.stderr.flush()
		stream.close()

	def install_script(self, context, name, url):
		_, _, path, _, _, _ = urlparse(url)
		fn = os.path.split(path)[-1]
		binpath = context.bin_path
		distpath = os.path.join(binpath, fn)
		# Download script into the env's binaries folder
		urlretrieve(url, distpath)
		progress = self.progress
		if self.verbose:
			term = '\n'
		else:
			term = ''
		if progress is not None:
			progress('Installing %s ...%s' % (name, term), 'main')
		else:
			sys.stderr.write('Installing %s ...%s' % (name, term))
			sys.stderr.flush()
		# Install in the env
		args = [context.env_exe, fn]
		p = Popen(args, stdout=PIPE, stderr=PIPE, cwd=binpath)
		t1 = Thread(target=self.reader, args=(p.stdout, 'stdout'))
		t1.start()
		t2 = Thread(target=self.reader, args=(p.stderr, 'stderr'))
		t2.start()
		p.wait()
		t1.join()
		t2.join()
		if progress is not None:
			progress('done.', 'main')
		else:
			sys.stderr.write('done.\n')
		# Clean up - no longer needed
		os.unlink(distpath)

	def add_install_url(self, url: str, name: str) -> None:
		'''
		Prepares the URL to be installed when using `create()`
		'''

		self.scripts_to_install.append([name, url])

	def add_install_from_pypi(self, package_name: str) -> None:
		'''
		Prepares a package from https://pypi.org to be installed when using `create()`
		'''

		self.scripts_to_install.append([package_name, PYPI_BASE_PROJECT_URL + package_name])


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


# Create virtual environment
venv_path = os.path.join(INSTALL_PATH, '.venv')

venv = VenvInstaller()
venv.add_install_from_pypi('flask')
venv.create(venv_path)


abs_script_path = os.path.abspath(os.path.join(INSTALL_PATH, 'command.py'))

subprocess.run(['chmod', '+x', abs_script_path])
subprocess.run(['sudo', 'ln', '-s', abs_script_path, COMMAND_PATH])
