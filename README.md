# Server/Client Application in Python

In this project I created several python scripts to simulate an application based on server/client architecture. Mainly server and client scripts transfer data via TCP and manage databases. 

## How to Run

- run ```pip install -r requirements.txt``` in your python environment.
- setup your MYSQL server and fill out .env file accordingly.
- run ```python create_database_and_key.py``` to create empty/dummy databases for Server and clients.
- run ```python server.py``` , ```python client1.py``` , ```python client2.py``` in different terminals in this order. (Server needs to be up first so clients could connect)

now you can play around with the application. Use different task options from server.py, remove/reconnect clients.
