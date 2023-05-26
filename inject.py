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
    return 200

def sign_out(id_chat, msg_id, chat_tm):
    cursor = db.db.cursor()

    query = f"INSERT INTO {db.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '2')

    cursor.execute(query, val)
    db.db.commit()
    print(cursor.rowcount)
    return 200

def init_data(user_id, username, admin_status):
    cursor = db.db.cursor()

    query = f"SELECT username FROM mentorku.userlist WHERE userid={user_id}"
    cursor.execute(query)
    data=cursor.fetchall()

    if(admin_status == "administrator" or admin_status == "creator"):
        status = 1
    else:
        status = 0

    if(data is None):
        query = f"INSERT INTO mentorku.userlist (userid, username, update_dt, active, admin_status) values (%s, %s, CURRENT_TIMESTAMP, 1, %d)"
        val = (user_id, username, int(status))
        cursor.execute(query, val)
        db.db.commit()
        return 200
    else:
        return 409