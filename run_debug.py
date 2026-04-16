from server import create_server
import random


def start_server():
	created_server = create_server()
	created_server.run(port=random.randint(5000, 9000), debug=True)


if __name__ == '__main__':
	start_server()
