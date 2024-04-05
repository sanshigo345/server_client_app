import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv(override=True)

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

    # Commit changes and close connection
    conn.commit()
    conn.close()    

def create_mysql_database():
    # Create MySQL database using SQLAlchemy
    mysql_username = os.getenv('MYSQL_USERNAME')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    mysql_host = os.getenv('MYSQL_HOST')
    mysql_port = int(os.getenv('MYSQL_PORT'))
    mysql_database = os.getenv('MYSQL_DATABASE')

    connection_string = f'mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/'
    print(f'Using {connection_string}')

    # Use NullPool for a connectionless connection (no connection pooling)
    engine = create_engine(connection_string, poolclass=NullPool)

    # Create a connection to execute SQL queries
    with engine.connect() as connection:
        existing_databases = connection.execute(text("SHOW DATABASES;"))
        existing_databases = [d[0] for d in existing_databases]
        print(f'Existing databases: {existing_databases}')

        if mysql_database not in existing_databases:
            connection.execute(text(f"CREATE DATABASE {mysql_database};"))

        connection.execute(text(f"USE {mysql_database};"))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS clients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                host VARCHAR(100) NOT NULL,
                port INT NOT NULL
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS personnel (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                surname VARCHAR(100) NOT NULL,
                ssn VARCHAR(11) NOT NULL
            );
        """))

        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_id INT NOT NULL,
                payload JSON NOT NULL,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            );
        """))

        # Insert dummy data into personnel table
        personnel_dummy_data = [
            ('Bugra', 'Ercan', '313-88-9999'),
            ('Sefa', 'Keles', '999-11-2222')
        ]

        for data in personnel_dummy_data:
            connection.execute(text("INSERT INTO personnel (name, surname, ssn) VALUES (:name, :surname, :ssn);"), {"name": data[0], "surname": data[1], "ssn": data[2]})

        # Commit the transaction explicitly
        connection.commit()

    engine.dispose()

if __name__ == "__main__":
    create_sqlite_database_client_one()
    create_sqlite_database_client_two()
    create_mysql_database()
    print("Databases for Server, client1 and client2 created.")
