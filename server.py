import socket
import os
from dotenv import load_dotenv
import threading
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from cryptography.fernet import Fernet

load_dotenv()

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

DATABASE_URI = f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

if MYSQL_PORT is None or MYSQL_HOST is None or MYSQL_DATABASE is None:
    raise ValueError("Server configuration probably is wrong. Please check it in the .env file.")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def send_message_to_client(message, client_host, client_port):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
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

# Function to handle client connections
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")

    # Receive data from client
    data = client_socket.recv(1024).decode()
    print(f"Received data from client {client_address}: {data}")

    # Process data (implement logic based on requirements)

    # Close client socket
    client_socket.close()
    print(f"Connection with {client_address} closed")

# Main function to start the server
def send_specific_personnel_to_client():
    while True:
        # Get personnel SSN from the user
        ssn = input("Enter personnel's SSN: ")

        # Get client name from the user
        client_name = input("Enter client's name: ")  # Assuming the client is identified by name

        # Query the personnel table to fetch name and surname based on SSN
        with engine.connect() as connection:
            # Query the personnel table to fetch name and surname based on SSN
            result = connection.execute("SELECT * FROM personnel WHERE SSN = ?", (ssn,))
            personnel_data = result.fetchone()  # Fetch the first row

            # Query the client table to check if the client exists
            result = connection.execute("SELECT * FROM clients WHERE NAME = ?", (client_name,))
            client_data = result.fetchone()  # Fetch the first row

        # Check if both personnel and client exist
        if personnel_data and client_data:
            # Extract name and surname from the query result
            personnel_name, personnel_surname = personnel_data
            client_port, client_host = client_data

            # Construct the message to send to the client
            message = {
                "action": "SAVE",  # Assuming the action is to save the personnel
                "personnel": {
                    "name": personnel_name,
                    "surname": personnel_surname,
                    "ssn": ssn
                }
            }

            send_message_to_client(message, client_host, client_port)
            
            break
        else:
            if not personnel_data:
                print("Personnel not found. Please try again.")
            if not client_data:
                print("Client not found. Please try again.")

def main():
    # Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((MYSQL_HOST, MYSQL_PORT))
    server_socket.listen(5)
    print(f"Server listening on {MYSQL_HOST}:{MYSQL_PORT}")

    try:
        while True:
            # Accept incoming connection
            client_socket, client_address = server_socket.accept()
            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

            print("Available tasks:")
            print("1. Send a specific personnel to a specific client.")
            print("2. Send a specific personnel to all clients.")
            print("3. Send all personnel to all clients.")
            print("4. Delete a specific personnel from a specific client.")
            print("5. Delete a specific personnel from all clients.")
            print("6. Delete all personnel from all clients.")
            print("7. Exit.")

            task = input("Enter the task number you want to perform (1, 2, 3, etc.): ")

            if task == "1":
                print("Performing task")

            elif task == "2":
                # Perform task 2
                print("Performing task 2...")
            elif task == "3":
                # Perform task 3
                print("Performing task 3...")
            elif task == "4":
                # Perform task 4
                print("Performing task 4...")
            elif task == "5":
                # Perform task 5
                print("Performing task 5...")
            elif task == "6":
                # Perform task 6
                print("Performing task 6...")
            else:
                print("Invalid task number. Please enter a valid task number.")

    except KeyboardInterrupt:
        print("Server shutting down")
        server_socket.close()
        
if __name__ == "__main__":
    main()
