import mysql.connector
from dotenv import load_dotenv
import os
import connector as db
load_dotenv()

def sign_in(id_chat, msg_id, chat_tm):
    cursor = db.db.cursor()

    query = f"INSERT INTO {db.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '1')

    cursor.execute(query, val)
    db.db.commit()

    print(cursor.rowcount)

def sign_out(id_chat, msg_id, chat_tm):
    cursor = db.db.cursor()

    query = f"INSERT INTO {db.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '2')

    cursor.execute(query, val)
    db.db.commit()

    print(cursor.rowcount)