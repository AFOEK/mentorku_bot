import datetime
from dateutil.relativedelta import *
from openpyxl import Workbook

def sign_in(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '1')

    cursor.execute(query, val)
    con.commit()
    print(cursor.rowcount)

def sign_out(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '2')

    cursor.execute(query, val)
    con.commit()
    print(cursor.rowcount)

def init_data(user_id, username, admin_status, real_name, con):
    cursor = con.cursor()

    query = f"SELECT username FROM mentorku.userlist WHERE userid={user_id}"
    cursor.execute(query)
    data=cursor.fetchone()
    print(data)
    
    if(admin_status == "administrator" or admin_status == "creator"):
        status = 1
    else:
        status = 0


    if(data is None):
        query = f"""INSERT INTO mentorku.userlist (userid, username, name, update_dt, in_dt, active, admin_status) values (%s, %s, %s,CURRENT_TIMESTAMP, TIME("07:00:00"), 1, %s)"""
        val = (user_id, username, real_name, int(status))
        cursor.execute(query, val)
        con.commit()
        return 200
    else:
        return 409
        
def get_admin_stat(userid, con):
    cursor = con.cursor()

    query = f"SELECT admin_status FROM mentorku.userlist WHERE userid = %s and active = %s"
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

    query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
    val = (today,)
    cursor.execute(query, val)
    return cursor

def get_time(id_chat, con):
    cursor = con.cursor()

    query =f"SELECT in_dt FROM mentorku.userlist where userid = {id_chat}"
    cursor.execute(query)
    data = cursor.fetchone()[0]
    return data

def get_data_week(con):
    today = datetime.date.today()
    week = datetime.date.today() + relativedelta(days=-7)
    cursor = con.cursor()

    query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
    val = (week,today)
    cursor.execute(query, val)
    return cursor

def get_data_month(con):
    today = datetime.date.today()
    month = datetime.date.today() + relativedelta(months=-1)
    cursor = con.cursor()

    query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
    val = (month,today)
    cursor.execute(query, val)
    return cursor

def get_data_year(con):
    today = datetime.date.today()
    year = datetime.date.today() + relativedelta(years=-1)
    cursor = con.cursor()

    query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
    val = (year,today)
    cursor.execute(query, val)
    return cursor

def get_data_today_excel(con):
    today = datetime.date.today()
    cursor = con.cursor()
    wb = Workbook()

    query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
    val = (today,)
    cursor.execute(query, val)
    result = cursor.fetchall()

    ws = wb.active
    ws.title = "Today Absention"
    ws.append(cursor.column_names)

    for row in result:
        ws.append(row)

    wb_name = "Mentorku attendance today"
    wb.save(wb_name+".xlsx")