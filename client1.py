import socket
import os
import sqlite3
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

with open("fernet_key.key", "rb") as key_file:
    fernet_key = key_file.read()

# Create a Fernet instance
cipher = Fernet(fernet_key)

CLIENT_DATABASE_FILE = "client_one_database.db"

# Connect to the SQLite database
conn = sqlite3.connect(CLIENT_DATABASE_FILE)
cursor = conn.cursor()

# Get server host and port from environment variables
SERVER_HOST = str(os.getenv("SERVER_HOST"))
SERVER_PORT = int(os.getenv("SERVER_PORT"))

def save_personnel(personnel):
    name = personnel.get("name")
    surname = personnel.get("surname")
    ssn = personnel.get("ssn")

    # Insert a new personnel record into the database
    cursor.execute("INSERT INTO personnel (NAME, SURNAME, SSN) VALUES (?, ?, ?)", (name, surname, ssn))
    conn.commit()
    print("Personnel saved successfully.")

def delete_personnel(personnel):
    ssn = personnel.get("ssn")
    # Delete a personnel record from the database based on SSN
    cursor.execute("DELETE FROM personnel WHERE SSN = ?", (ssn,))
    conn.commit()
    print("Personnel deleted successfully.")

# Function to handle server messages
def handle_server_message(client_socket):
    try:
        while True:
            # Receive encrypted message from server
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            
            # Decrypt the message
            decrypted_message = cipher.decrypt(encrypted_message).decode()

            # Parse JSON message
            message_data = json.loads(decrypted_message)

            # Extract action and personnel data from message
            action = message_data.get("action")
            personnel = message_data.get("personnel")

            # Perform action based on message content
            if action == "save":
                save_personnel(personnel)
            elif action == "delete":
                delete_personnel(personnel)
            else:
                print("Unknown action received from server.")

    except KeyboardInterrupt:
        print("Client shutting down")
    finally:
        client_socket.close()

# Main function to start the client
def main():
    try:
        # Create socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

        # Start receiving messages from server
        handle_server_message(client_socket)

    except KeyboardInterrupt:
        print("Client shutting down")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
