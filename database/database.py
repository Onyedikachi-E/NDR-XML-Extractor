import uuid
import mysql.connector as sql
from mysql.connector import Error


def generate_uuid():
    return str(uuid.uuid4())


def connect_to_database() -> sql.MySQLConnection | None:
    "To create a connection string to the database using the correct credentials."
    try:
        connection = sql.connect(
            host='localhost',
            user='admin',
            password='Admin123',
            database='owaza_db'
        )
        if connection.is_connected():
            return connection
        
        else:
            print("Connection failed.")
            return None
    except Error as e:
        print("Error:", e)
        return None