import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

def db_connect():
    DB_ADD = ''.join(os.environ.get("DB_ADD")),
    DB_USER = ''.join(os.environ.get("DB_USER")),
    DB_PASSWORD = ''.join(os.environ.get("DB_PASSWORD")),
    DB_NAME = ''.join(os.environ.get("DB_NAME"))


    db = mysql.connector.connect(
        host = DB_ADD,
        user = DB_USER,
        password = DB_PASSWORD,
        database = DB_NAME
    )

    return db