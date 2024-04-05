# Server/Client Application in Python

This project comprises multiple Python scripts designed to emulate an application based on a server/client architecture. The server and client scripts primarily facilitate data transfer via TCP and manage databases.

## Getting Started

Follow these steps to set up and run the application:

### Prerequisites

Ensure you have Python and MySQL installed on your system.

### Installation

Install the required dependencies by running the following command in your Python environment:
- ```pip install -r requirements.txt```

Set up your MySQL server and configure the .env file with the appropriate credentials.

## Usage

Execute the following command to create empty or dummy databases for both the server and clients:
- ```python create_database_and_key.py```

Start the server by running:
- ```python server.py```

Run the client scripts in separate terminals, starting with client1.py and then client2.py:
-```python client1.py``` and ```python client2.py```

## Features

- The server allows interaction with clients through various task options provided in server.py.
0. Show personnel, clients and messages
1. Send a specific personnel to a specific client.
2. Send a specific personnel to all clients.
3. Send all personnel to all clients.
4. Delete a specific personnel from a specific client.
5. Delete a specific personnel from all clients.
6. Delete all personnel from all clients.
7. Exit.

- The clients accepts these messages and manage their databases accordingly. Client tasks include:
1. Save a personnel after receiving a save message from the server.
2. Delete a personnel after receiving a delete message from the server.

# Technical Overview of Project

## Python Sockets

The project implements a server/client architecture using Python sockets for communication between clients and the server. Sockets facilitate real-time interaction between clients and the server, enabling instantaneous communication and responsiveness. Moreover, Python sockets are platform-independent, ensuring seamless communication across different operating systems without compatibility issues. By incorporating Python sockets into the architecture, the project enhances its network communication capabilities, enabling efficient and reliable data exchange between different components of the application.

## Usage of MySQL and SQLite

The server component of the application utilizes MySQL for database operations, providing a reliable and scalable solution for managing data. On the other hand, clients utilize SQLite for local data storage, ensuring portability and independence from the server. This setup allows for efficient handling of data on both the server and client sides, optimizing performance and ensuring data integrity throughout the application.

## Object-Relational Mapping (ORM) with SQLAlchemy

The project utilizes SQLAlchemy, an ORM library for Python, to interact with the database, providing several benefits. ORM abstraction allows developers to treat database entities as Python objects, simplifying database operations and reducing the reliance on raw SQL queries. SQLAlchemy supports multiple database engines, facilitating seamless migration between different systems without extensive code modifications. Additionally, ORM promotes code maintainability by abstracting database details, resulting in cleaner and more scalable code.

## Encryption with Fernet Key

To ensure secure communication, the project employs Fernet symmetric key cryptography for message encryption, offering several benefits. Fernet encryption safeguards sensitive data, such as messages exchanged between the server and clients, ensuring confidentiality and protection against unauthorized access. Its high-level API simplifies integration into the application, requiring minimal cryptographic expertise. Moreover, Fernet encryption strikes a balance between security and performance, making it suitable for real-time applications.

## Multithreading in Server

The server component utilizes multithreading to concurrently handle connections from multiple clients, ensuring responsiveness and offering several benefits. Multithreading enables the server to process multiple client requests simultaneously, enhancing system throughput and responsiveness. This improves the user experience by allowing seamless interaction with the server, even during high client activity periods. Additionally, multithreading optimizes resource utilization by efficiently managing system resources, ensuring consistent server responsiveness under varying workload conditions.

## Usage of .env for Configuration

The project utilizes .env files to securely manage configuration variables, offering several advantages. Firstly, it enhances security by safeguarding sensitive information like database credentials and encryption keys from exposure in version-controlled repositories. Secondly, .env files simplify configuration by providing a centralized mechanism for adjusting environment-specific variables without altering the source code. Lastly, separating configuration details from the codebase enhances portability, facilitating seamless deployment across various environments without the need to hardcode configuration settings.

## Storing Messages in JSON

Storing log messages in JSON is advantageous because it provides a structured format that encapsulates key information within each log entry. This structured approach allows for easier parsing and analysis of log data, facilitating tasks such as searching, filtering, and extracting relevant information. Additionally, JSON log messages are highly compatible with a wide range of logging systems and tools, enabling seamless integration into existing logging infrastructures and simplifying log management processes. This structured representation enhances readability and maintainability, making it easier for developers and administrators to interpret and troubleshoot log data effectively.