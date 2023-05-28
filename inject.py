import mysql.connector
from dotenv import load_dotenv
import os
import connector as db
import datetime
import tzlocal
load_dotenv()

def sign_in(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO {db.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '1')

    cursor.execute(query, val)
    db.db.commit()
    print(cursor.rowcount)
    return 200

def sign_out(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO {db.DB_NAME}.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '2')

    cursor.execute(query, val)
    db.db.commit()
    print(cursor.rowcount)
    return 200

def init_data(user_id, username, admin_status, con):
    cursor = con.cursor()

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
    
def get_admin_stat(userid, con):
    cursor = con.cursor()

    query = f"SELECT admin_status FROM mentorku.userlist WHERE userid = %s and active = %d"
    val = (userid, 1)
    cursor.execute(query, val)
    data = cursor.fetchone()[0]
    if(data == 1):
        return True
    else:
        return False

def get_data_today(con):
    today = datetime.date.today()
    cursor = con.cursor()

    query = f"SELECT * FROM mentorku.absensi WHERE DATE(time_stamp) = %s"
    val = (today)
    cursor.execute(query, val)
    data = cursor.fetchall()
    return data

