import os
import sqlite3
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_sqlite_database_client_one():
    # Connect to SQLite database
    conn = sqlite3.connect('client_one_database.db')
    cursor = conn.cursor()

    # Create personnel table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personnel (
        ID INTEGER PRIMARY KEY,
        NAME TEXT,
        SURNAME TEXT,
        SSN TEXT
    )
    ''')

    # Insert dummy data into the personnel table
    sqlite_personel_dummy_data = [
        ('Michael', 'Davis', '111-22-3333'),
        ('Sarah', 'Wilson', '444-55-6666')
        # ('David', 'Taylor', '777-88-9999'),
        # ('Emily', 'Clark', '000-11-2222'),
        # ('Matthew', 'Allen', '333-44-5555')
    ]

    cursor.executemany('''
    INSERT INTO personnel (NAME, SURNAME, SSN)
    VALUES (?, ?, ?)
    ''', sqlite_personel_dummy_data)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def create_sqlite_database_client_two():
    # Connect to SQLite database
    conn = sqlite3.connect('client_two_database.db')
    cursor = conn.cursor()

    # Create personnel table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personnel (
        ID INTEGER PRIMARY KEY,
        NAME TEXT,
        SURNAME TEXT,
        SSN TEXT
    )
    ''')

    # Insert dummy data into the personnel table
    sqlite_personel_dummy_data = [
        ('David', 'Taylor', '777-88-9999'),
        ('Emily', 'Clark', '000-11-2222')
        # ('Matthew', 'Allen', '333-44-5555')
    ]

    cursor.executemany('''
    INSERT INTO personnel (NAME, SURNAME, SSN)
    VALUES (?, ?, ?)
    ''', sqlite_personel_dummy_data)

    # Commit changes and close connection
    conn.commit()
    conn.close()    

def create_mysql_database():
    # Create MySQL database using SQLAlchemy
    mysql_username = os.getenv('MYSQL_USERNAME')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_port = int(os.getenv('SERVER_PORT'))
    mysql_host = str(os.getenv('SERVER_HOST'))
    mysql_database = os.getenv('MYSQL_DATABASE')

    connection_string = f'mysql://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}'
    engine = create_engine(connection_string)

    with engine.connect() as connection:

        connection.execute(f'CREATE DATABASE IF NOT EXISTS {mysql_database}')

        connection.execute(f'USE {mysql_database}')

        connection.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(100),
            HOST VARCHAR(100),
            PORT INT
        )
        ''')

        connection.execute('''
        CREATE TABLE IF NOT EXISTS personnel (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            NAME VARCHAR(100),
            SURNAME VARCHAR(100),
            SSN VARCHAR(11)
        )
        ''')

        connection.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            CLIENT_ID INT,
            PAYLOAD JSON,
            FOREIGN KEY (CLIENT_ID) REFERENCES clients(ID)
        )
        ''')

        mysql_clients_dummy_data = [
            ('Client1', '127.0.0.1', 8000),
            ('Client2', '127.0.0.1', 8001),
            ('Client3', '127.0.0.1', 8002)
        ]

        connection.execute('''
        INSERT INTO clients (NAME, HOST, PORT)
        VALUES (%s, %s, %s)
        ''', mysql_clients_dummy_data)

        mysql_personnel_dummy_data = [
            ('John', 'Doe', '123-45-6789'),
            ('Jane', 'Smith', '987-65-4321'),
            ('Alice', 'Johnson', '456-78-9012'),
            ('Bob', 'Williams', '789-01-2345'),
            ('Eve', 'Brown', '012-34-5678')
        ]

        connection.execute('''
        INSERT INTO personnel (NAME, SURNAME, SSN)
        VALUES (%s, %s, %s)
        ''', mysql_personnel_dummy_data)


if __name__ == "__main__":
    create_sqlite_database_client_one()
    create_sqlite_database_client_two()
    create_mysql_database()
    print("Dummy databases for client1 and client2 and server created.")
