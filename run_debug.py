from server import create_server
import random

created_server = create_server()
created_server.run(port=random.randint(5000, 9000), debug=True)
