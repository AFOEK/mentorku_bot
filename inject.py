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

def init_data(user_id, username, admin_status, real_name, chat_id, con):
    cursor = con.cursor()

    query = f"SELECT username FROM mentorku.userlist WHERE userid={user_id}"
    cursor.execute(query)
    data=cursor.fetchone()
    
    if(admin_status == "administrator" or admin_status == "creator"):
        status = 1
    else:
        status = 0


    if(data is None):
        query = f"""INSERT INTO mentorku.userlist (userid, chat_room_id, username, name, update_dt, in_dt, active, admin_status) values (%s, %s, %s, %s, CURRENT_TIMESTAMP, TIME("07:00:00"), 1, %s)"""
        val = (user_id, chat_id, username, real_name, int(status))
        cursor.execute(query, val)
        con.commit()
        return 200
    elif(data is not None):
        query = f"""UPDATE mentorku.userlist SET update_dt = CURRENT_TIMESTAMP, chat_room_id = "%s" WHERE userid = {user_id}"""
        val = (chat_id,)
        cursor.execute(query, val)
        con.commit()
        return 204
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
        case "1d" | "now":
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
            val = (date,)
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=+7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,week)
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,month)
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,year)
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
        case "1d" | "now":
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
            val = (date,)
            ws.title = "Today attendances"
            periode = "today"
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=+7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,week)
            ws.title = "This week attendances"
            periode = "week"
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,month)
            ws.title = "This month attendances"
            periode = "month"
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,year)
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
    return str(periode)

def sick(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '3')

    cursor.execute(query, val)
    con.commit()
    print(cursor.rowcount)


def get_leave_status(userid, con):
    cursor = con.cursor()

    query = f"SELECT * FROM mentorku.absensi WHERE MONTH(time_stamp) = MONTH(CURDATE()) AND status = 4 AND userid = {userid}"
    cursor.execute(query)
    data = cursor.fetchall()

    if not data:
        return True
    else:
        return False

def leave(id_chat, msg_id, chat_tm, dur, con):
    cursor = con.cursor()
    
    for i in range (1, int(dur) + 1):
        times = chat_tm + relativedelta(days=+i)
        query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
        val = (id_chat, msg_id, times, '4')
        cursor.execute(query, val)
        print("days " + str(i))

    con.commit()
    return True

def set_user_time(username, in_dt, con):
    cursor = con.cursor()
    query =f"""SELECT in_dt FROM mentorku.userlist where username = "{username}";"""
    cursor.execute(query)
    data = cursor.fetchall()
    
    if not data:
        return 409
    else:
        query = f"""UPDATE mentorku.userlist SET in_dt = %s WHERE username = %s"""
        val = (in_dt,username)
        cursor.execute(query, val)
        con.commit()
        return 200

def check_in_dt(con):
    cursor = con.cursor()
    query = f"SELECT userid, username, chat_room_id, in_dt FROM mentorku.userlist WHERE active = 1"
    cursor.execute(query)
    data = cursor.fetchall()
    return data

def recent_signin(con):
    cursor = con.cursor()
    query = f"""SELECT u.userid, u.username, u.chat_room_id, u.in_dt, a.time_stamp FROM mentorku.userlist u JOIN mentorku.absensi a ON u.userid = a.userid WHERE u.active = 1 AND a.status = 1 AND DATE(a.time_stamp) = DATE(CURRENT_TIMESTAMP())"""
    cursor.execute(query)
    data = cursor.fetchall()
    return data