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

def sign_in(id_chat, msg_id, chat_tm):
    cursor = db_connect.db.cursor()

    query = f"INSERT INTO {db_connect.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, 1)"
    val = (id_chat, msg_id, chat_tm)

    cursor.execute(query, val)
    db_connect.db.commit()

    print(cursor.rowcount)

def sign_out(id_chat, msg_id, chat_tm):
    cursor = db_connect.db.cursor()

    query = f"INSERT INTO {db_connect.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, 2)"
    val = (id_chat, msg_id, chat_tm)

    cursor.execute(query, val)
    db_connect.db.commit()

    print(cursor.rowcount)