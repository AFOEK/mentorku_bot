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
    
def get_time(id_chat, con):
    cursor = con.cursor()

    query =f"SELECT in_dt FROM mentorku.userlist where userid = {id_chat}"
    cursor.execute(query)
    data = cursor.fetchone()[0]
    return data

def get_data(con, args):
    cursor = con.cursor()
    date = datetime.date.today()
    match args:
        case "1d":
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
            val = (date,)
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=-7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (week,date)
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=-1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (month,date)
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=-1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (year,date)
        case _:
            return 409

    cursor.execute(query, val)
    return cursor

def get_data_excel(con, args):
    date = datetime.date.today()
    cursor = con.cursor()
    wb = Workbook()
    ws = wb.active

    match args:
        case "1d":
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
            val = (date,)
            ws.title = "Today attendances"
            periode = "today"
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=-7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (week,date)
            ws.title = "This week attendances"
            periode = "week"
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=-1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (month,date)
            ws.title = "This month attendances"
            periode = "month"
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=-1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (year,date)
            ws.title = "This year attendances"
            periode = "year"
        case _:
            return 409

    cursor.execute(query, val)
    result = cursor.fetchall()

    ws.append(cursor.column_names)

    for row in result:
        ws.append(row)

    wb_name = "Mentorku attendance " + periode
    wb.save(wb_name+".xlsx")
    return periode