COLOR_NOTICE = '\033[90m'
COLOR_ERROR = '\033[91m'
COLOR_END = '\033[0m'


def notice(*messages) -> None:
	print(
		COLOR_NOTICE +
		'NOTICE:',
		' '.join(messages) +
		COLOR_END
	)

def error(*messages) -> None:
	print(
		COLOR_ERROR +
		'ERROR:',
		' '.join(messages) +
		COLOR_END
	)
	exit(1)
