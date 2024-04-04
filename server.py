import json
import socket
import os
from dotenv import load_dotenv
import threading
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet

load_dotenv(override=True)

# Read the Fernet key from the file
with open("fernet_key.key", "rb") as f:
    key = f.read()

# Initialize the Fernet object with the key
fernet = Fernet(key)

# Get MySQL credentials from environment variables
MYSQL_USERNAME = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

connection_string = f"mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Create SQLAlchemy engine and session
engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Client(name={self.name}, host={self.host}, port={self.port})>"

class Personnel(Base):
    __tablename__ = 'personnel'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    ssn = Column(String(11), nullable=False, unique=True)

    def __repr__(self):
        return f"<Personnel(name={self.name}, surname={self.surname}, ssn={self.ssn})>"


def get_next_client_name(session):
    try:
        # Query the clients table to get the maximum client ID
        max_id = session.query(func.max(Client.id)).scalar()

        # If there are no clients in the database, start with 1
        if max_id is None:
            return "Client #1"

        # Increment the maximum client ID to get the next client ID
        next_id = max_id + 1

        # Check if the next ID is already taken by a disconnected client
        existing_client = session.query(Client).filter_by(id=next_id).first()

        if existing_client is None:
            return f"Client #{next_id}"
        else:
            # Find the first available ID for the next client
            while True:
                next_id += 1
                existing_client = session.query(Client).filter_by(id=next_id).first()
                if existing_client is None:
                    return f"Client #{next_id}"
    except SQLAlchemyError as e:
        print(f"Error occurred while getting next client name: {e}")
        return None

def send_message_to_client(message, client_host, client_port):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        print(f"trying to connect to client {client_host}:{client_port}")
        # Connect to the client
        client_socket.connect((client_host, client_port))

        # Encrypt the message with Fernet
        encrypted_message = fernet.encrypt(message.encode())

        # Send the encrypted message to the client
        client_socket.sendall(encrypted_message)

        print("Message sent successfully to client.")
    except Exception as e:
        print(f"Error sending message to client: {e}")
    finally:
        # Close the client socket
        client_socket.close()

def accept_connections(server_socket):
    while True:
        # Accept incoming connection
        client_socket, client_address = server_socket.accept()

        # Create a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

def handle_client(client_socket, client_address):

    client_host = client_address[0]
    client_port = client_address[1]

    print(f"Connection from {client_host} and {client_port}")

    session = Session()

    try:
        # Get the next client name
        client_name = get_next_client_name(session)

        # Create a new Client object
        new_client = Client(name=client_name, host=client_host, port=client_port)

        # Add the new client to the database session
        session.add(new_client)
        session.commit()

        print(f"Added client {client_name} to the database.")

        while True:
            try:
                data = client_socket.recv(1)
                if not data:
                    print("client disconnected")
                    break
            except ConnectionResetError:
                print(f"Connection from {client_host} and {client_port} closed.")
                break

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error occurred while adding client to the database: {e}")
    finally:
        # Close the session and client socket
        session.close()
        client_socket.close()
        print(f"Connection with {client_address} closed.")
        try:
            session.query(Client).filter_by(host=client_host, port=client_port).delete()
            session.commit()
            print(f"Removed client from the database: {client_host} and {client_port}")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error occurred while removing client from the database: {e}")

def send_specific_personnel_to_client():
    while True:
        # Get personnel SSN from the user
        ssn = input("Enter personnel's SSN (ex: 123-45-6789): ")

        # Get client name from the user
        client_name = input("Enter client's name: ")

        session = Session()

        try:
            personnel = session.query(Personnel).filter_by(ssn=ssn).first()
            client = session.query(Client).filter_by(name=client_name).first()

            if personnel and client:
                personnel_name = personnel.name
                personnel_surname = personnel.surname
                client_port = client.port
                client_host = client.host

                message = {
                    "action": "SAVE",
                    "personnel": {
                        "name": personnel_name,
                        "surname": personnel_surname,
                        "ssn": ssn
                    }
                }

                send_message_to_client(message, client_host, client_port)

                print(f"used {personnel_name} {personnel_surname} and {client_port} {client_host}")

                break
            else:
                if not personnel:
                    print("Personnel not found. Please try again.")
                if not client:
                    print("Client not found. Please try again.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error occurred while adding client to the database: {e}")
        finally:
            session.close()

def send_specific_personnel_to_all_clients():
    while True:
        # Get personnel SSN from the user
        ssn = input("Enter personnel's SSN (ex: 123-45-6789): ")

        # Query the personnel table to fetch name and surname based on SSN
        with engine.connect() as connection:
            # Query the personnel table to fetch name and surname based on SSN
            result = connection.execute("SELECT * FROM personnel WHERE SSN = ?", (ssn,))
            personnel_data = result.fetchone()  # Fetch the first row

        # Check if personnel exists
        if personnel_data:
            # Extract name and surname from the query result
            personnel_name, personnel_surname = personnel_data

            # Construct the message to send to all clients
            message = {
                "action": "SAVE",  # Assuming the action is to save the personnel
                "personnel": {
                    "name": personnel_name,
                    "surname": personnel_surname,
                    "ssn": ssn
                }
            }

            # Query all clients from the database
            result = connection.execute("SELECT * FROM clients")
            all_clients = result.fetchall()

            # Send the message to each client
            for client_data in all_clients:
                client_host, client_port = client_data

                send_message_to_client(message, client_host, client_port)

            break
        else:
            print("Personnel not found. Please try again.")

def send_all_personnel_to_all_clients():
    try:
        # Query all personnel from the database
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM personnel")
            all_personnel = result.fetchall()

        all_personnel_json = json.dumps(all_personnel)
        # Construct the message to send to clients
        message = {
            "action": "SAVE_ALL_PERSONNEL",
            "personnel": all_personnel_json
        }

        # Get all clients from the database
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM clients")
            all_clients = result.fetchall()

        # Send the encrypted message to each client
        for client_data in all_clients:
            client_host, client_port = client_data
            send_message_to_client(message, client_host, client_port)

        print("All personnel sent successfully to all clients.")
    except Exception as e:
        print(f"Error sending personnel to clients: {e}")

def delete_specific_personnel_from_client():
    while True:
        # Get personnel SSN from the user
        ssn = input("Enter personnel's SSN (ex: 123-45-6789): ")

        # Get client name from the user
        client_name = input("Enter client's name: ")

        # Query the client table to check if the client exists
        with engine.connect() as connection:
            # Query the client table to check if the client exists
            result = connection.execute("SELECT * FROM clients WHERE NAME = ?", (client_name,))
            client_data = result.fetchone()  # Fetch the first row

        # Check if client exist
        if client_data:

            client_port, client_host = client_data

            # Construct the message to send to the client
            message = {
                "action": "DELETE",
                "personnel": {
                    "ssn": ssn
                }
            }

            # Send the message to the specific client
            send_message_to_client(message, client_host, client_port)

            print("Personnel deletion request sent to the client.")
            break
        else:
            print("Client not found. Please try again.")

def delete_specific_personnel_from_all_clients():
    try:
        # Get personnel SSN from the user
        ssn = input("Enter personnel's SSN (ex: 123-45-6789): ")

        message = {
            "action": "DELETE",
            "personnel": {
                "ssn": ssn
            }
        }

        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM clients")
            all_clients = result.fetchall()

        # Send the encrypted message to each client
        for client_data in all_clients:
            client_host, client_port = client_data
            send_message_to_client(message, client_host, client_port)

    except Exception as e:
        print(f"Error deleting personnel from clients: {e}")

def delete_all_personnel_from_all_clients():
    try:
        message = {
            "action": "DELETE_ALL_PERSONNEL"
        }

        # Get all clients from the database
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM clients")
            all_clients = result.fetchall()

        # Send the message to each client
        for client_data in all_clients:
            client_host, client_port = client_data
            send_message_to_client(message, client_host, client_port)

        print("Packet sent to all clients")
    except Exception as e:
        print(f"Error sending personnel to clients: {e}")    

# Main function to start the server
def main():
    # Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    connection_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    connection_thread.start()

    try:
        while True:
            print("Available tasks:")
            print("1. Send a specific personnel to a specific client.")
            print("2. Send a specific personnel to all clients.")
            print("3. Send all personnel to all clients.")
            print("4. Delete a specific personnel from a specific client.")
            print("5. Delete a specific personnel from all clients.")
            print("6. Delete all personnel from all clients.")
            print("7. Exit.")

            task = input("Enter the task number you want to perform (0, 1, 2, etc.): ")

            if task == "0":
                print("show tables")
            elif task == "1":
                print("Performing send a specific personnel to a specific client.")
                send_specific_personnel_to_client()
            elif task == "2":
                print("Performing send a specific personnel to all clients.")
                send_specific_personnel_to_all_clients()
            elif task == "3":
                print("Performing send all personnel to all clients.")
                send_all_personnel_to_all_clients()
            elif task == "4":
                print("Performing delete a specific personnel from a specific client.")
                delete_specific_personnel_from_client()
            elif task == "5":
                print("Performing delete a specific personnel from all clients.")
                delete_specific_personnel_from_all_clients()
            elif task == "6":
                print("Performing delete all personnel from all clients.")
                delete_all_personnel_from_all_clients()
            elif task == "7":
                print("Exiting...")
                break
            else:
                print("Invalid task number. Please enter a valid task number.")

    except KeyboardInterrupt:
        print("Server shutting down")
        server_socket.close()

    quit()

if __name__ == "__main__":
    main()
