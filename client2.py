import socket
import threading
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

CLIENT_DATABASE_FILE = "client_two_database.db"

# Get server host and port from environment variables
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

def listen_to_server(client_socket):
    try:
        while True:
            # Receive data from the server
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                print('Disconnected from server')
                break
            decrypted_message = cipher.decrypt(encrypted_message)
            decrypted_message_str = decrypted_message.decode()
            message_dict = json.loads(decrypted_message_str)

            print(f"message_dict {message_dict}")

            action = message_dict.get("action")
            personnel = message_dict.get("personnel")

            # Perform action based on message content
            if action == "SAVE":
                save_personnel(personnel)
            elif action == "DELETE":
                delete_personnel(personnel)
                print("Personnel deleted successfully.")
            elif action == "SAVE_ALL":
                for personnel in message_dict["personnel"]:
                    save_personnel(personnel)
            elif action == "DELETE_ALL":
                conn = sqlite3.connect(CLIENT_DATABASE_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM personnel")
                conn.commit()
                conn.close()     
                print("All Personnel deleted successfully.")           
            else:
                print("Unknown action received from server.")

    except Exception as e:
        print("Error:", e)
    finally:
        # Close the socket when the server stops sending data
        client_socket.close()

def save_personnel(personnel):
    name = personnel.get("name")
    surname = personnel.get("surname")
    ssn = personnel.get("ssn")

    conn = sqlite3.connect(CLIENT_DATABASE_FILE)
    cursor = conn.cursor()

    # Insert a new personnel record into the database
    cursor.execute("INSERT INTO personnel (NAME, SURNAME, SSN) VALUES (?, ?, ?)", (name, surname, ssn))
    conn.commit()
    print(f"Personnel {name} {surname} saved successfully.")

def delete_personnel(personnel):
    ssn = personnel.get("ssn")

    conn = sqlite3.connect(CLIENT_DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM personnel WHERE SSN = ?", (ssn,))
    conn.commit()

# Main function to start the client
def main():
    try:
        # Create socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Connect to server
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to server {SERVER_HOST}:{SERVER_PORT}")

        listen_thread = threading.Thread(target=listen_to_server, args=(client_socket,))
        listen_thread.start()

    except KeyboardInterrupt:
        print("Client shutting down")

if __name__ == "__main__":
    main()
