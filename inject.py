import datetime
from dateutil.relativedelta import *
from openpyxl import Workbook
import logging as log

def set_var(con, tz):
    log.info(f"Set connection timeout, wait_timeout, interactive_timeout for 8 hours and set session timezone to '{tz}'")
    cursor = con.cursor()
    query1 = "SET GLOBAL connect_timeout=64800;"
    query2 = "SET SESSION wait_timeout=64800;"
    query3 = "SET SESSION interactive_timeout=64800;"
    query4 = f"SET @@SESSION.time_zone = '{tz}';"
    query5 = "SET SESSION sql_mode='';"
    cursor.execute(query1)
    cursor.execute(query2)
    cursor.execute(query3)
    cursor.execute(query4)
    cursor.execute(query5)
    con.commit()
    cursor.close()

def check_userlist_empty(id_chat, con):
    cursor = con.cursor()
    query = f"SELECT * FROM mentorku.userlist WHERE userid = %s"
    val = (id_chat,)
    cursor.execute(query, val)
    data = cursor.fetchall()
    if not data:
        log.info(f"User list empty, return {404}, function name {check_userlist_empty.__name__}")
        cursor.close()
        return 404
    else:
        log.info(f"User list populated, return {200}, function name {check_userlist_empty.__name__}")
        cursor.close()
        return 200

def check_onleave(id_chat, con):
    cursor = con.cursor()
    query = f"SELECT id FROM mentorku.absensi WHERE (userid = %s AND DATE(time_stamp) = DATE(CURRENT_TIMESTAMP)) AND (status = 3 OR status = 4)"
    val = (id_chat,)
    cursor.execute(query, val)
    data = cursor.fetchall()
    if not data:
        log.info(f"Leave notice was empty, return {404}, function name {check_onleave.__name__}")
        cursor.close()
        return 404
    else:
        log.info(f"Leave notice populated, return {200}, function name {check_onleave.__name__}")
        cursor.close()
        return 200

def sign_in(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()
    query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '1')
    cursor.execute(query, val)
    con.commit()
    cursor.close()
    log.info(f"User wrote into database with row count: {cursor.rowcount}, function name {sign_in.__name__}")

def sign_out(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor(buffered=True)
    query = f"SELECT * FROM mentorku.absensi WHERE userid = {id_chat} AND status = 1 AND DATE(time_stamp) = DATE(CURRENT_TIMESTAMP)"
    cursor.execute(query)
    data = cursor.fetchone()
    if data is not None:
        query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
        val = (id_chat, msg_id, chat_tm, '2')
        cursor.execute(query, val)
        con.commit()
        log.info(f"User wrote into database with row count: {cursor.rowcount}, with return value {200}, function name {sign_out.__name__}")
        cursor.close()
        return 200
    else:
        log.info(f"User didn't sign in before, with return value {404}, function name {sign_out.__name__}")
        cursor.close()
        return 404


def init_data(user_id, username, admin_status, real_name, chat_id, con):
    cursor = con.cursor()

    query = f"SELECT username FROM mentorku.userlist WHERE userid={user_id}"
    cursor.execute(query)
    data=cursor.fetchone()
    
    if(admin_status == "administrator" or admin_status == "creator" or admin_status == "owner"):
        status = 1
    else:
        status = 0


    if(data is None):
        query = f"""INSERT INTO mentorku.userlist (userid, chat_room_id, username, name, update_dt, in_dt, active, admin_status) values (%s, %s, %s, %s, CURRENT_TIMESTAMP, TIME("07:00:00"), 1, %s)"""
        val = (user_id, chat_id, username, real_name, int(status))
        cursor.execute(query, val)
        con.commit()
        log.info(f"User wrote into database with row count: {cursor.rowcount}, function name {init_data.__name__} with return 200")
        cursor.close()
        return 200
    elif(data is not None):
        query = f"""UPDATE mentorku.userlist SET update_dt = CURRENT_TIMESTAMP, chat_room_id = "%s" WHERE userid = {user_id}"""
        val = (chat_id,)
        cursor.execute(query, val)
        con.commit()
        log.info(f"User updated into database with row count: {cursor.rowcount}, function name {init_data.__name__} with return 204")
        cursor.close()
        return 204
    else:
        log.info(f"No data write, function name {init_data.__name__} with return 409")
        cursor.close()
        return 409

        
def get_admin_stat(userid, con):
    cursor = con.cursor()

    query = f"SELECT admin_status FROM mentorku.userlist WHERE userid = %s and active = %s"
    val = (userid, 1)
    cursor.execute(query, val)
    data = cursor.fetchone()[0]
    if(data == 1):
        log.info(f"Get admin status {True}, with function name {get_admin_stat.__name__}")
        cursor.close()
        return True
    else:
        log.info(f"Get admin status {False}, with function name {get_admin_stat.__name__}")
        cursor.close()
        return False
    
def get_time(id_chat, con):
    cursor = con.cursor()

    query =f"SELECT in_dt FROM mentorku.userlist where userid = {id_chat}"
    cursor.execute(query)
    data = cursor.fetchone()[0]
    log.info(f"Get in time, with function name {get_time.__name__}")
    cursor.close()
    return data

def get_data(con, args):
    cursor = con.cursor()
    date = datetime.date.today()
    match args:
        case "1d" | "now":
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) = %s"
            val = (date,)
            log.info(f"Get data from view for 1 day")
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=+7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,week)
            log.info(f"Get data from view for 7 day")
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,month)
            log.info(f"Get data from view for 30 day")
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,year)
            log.info(f"Get data from view for 1 year")
        case _:
            log.info(f"No data can be get")
            return 409

    cursor.execute(query, val)
    log.info(f"Return data from database with row count: {cursor.rowcount}, from function {get_data.__name__}")
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
            log.info(f"Get data from view for 1 day")
        case "1w" | "7d":
            week = datetime.date.today() + relativedelta(days=+7)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,week)
            ws.title = "This week attendances"
            periode = "week"
            log.info(f"Get data from view for 7 day")
        case "1m" | "30d":
            month = datetime.date.today() + relativedelta(months=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,month)
            ws.title = "This month attendances"
            periode = "month"
            log.info(f"Get data from view for 30 day")
        case "1y" | "12m":
            year = datetime.date.today() + relativedelta(years=+1)
            query = f"SELECT * FROM mentorku.view_absensi WHERE DATE(time_stamp) BETWEEN %s and %s"
            val = (date,year)
            ws.title = "This year attendances"
            periode = "year"
            log.info(f"Get data from view for 1 year")
        case _:
            log.info(f"No data can be get")
            return 409

    cursor.execute(query, val)
    result = cursor.fetchall()

    ws.append(cursor.column_names)

    for row in result:
        ws.append(row)

    wb_name = "Mentorku attendance " + periode
    wb.save(wb_name+".xlsx")
    log.info(f"Saved a excel file with name {wb_name}.excel, with function name {get_data_excel.__name__}")
    cursor.close()
    return str(periode)

def sick(id_chat, msg_id, chat_tm, con):
    cursor = con.cursor()

    query = f"INSERT INTO mentorku.absensi (userid, chat_id, time_stamp, status) Values (%s, %s, %s, %s)"
    val = (id_chat, msg_id, chat_tm, '3')

    cursor.execute(query, val)
    con.commit()
    cursor.close()
    log.info(f"User inserted data into database with row count: {cursor.rowcount}, function name: {sick.__name__}")


def get_leave_status(userid, con):
    cursor = con.cursor()
    query = f"SELECT * FROM mentorku.absensi WHERE MONTH(time_stamp) = MONTH(CURDATE()) AND status = 4 AND userid = {userid}"
    cursor.execute(query)
    cursor.fetchall()
    absensi_rc = cursor.rowcount

    query = f"SELECT * FROM mentorku.approval WHERE MONTH(time_stamp) = MONTH(CURDATE()) AND status = 2 AND userid = {userid}"
    cursor.execute(query)
    cursor.fetchall()
    approval_rc = cursor.rowcount

    if(absensi_rc >= 3 and approval_rc >= 2):
        log.info(f"Get leave status with return {False}, with function name {get_leave_status.__name__}")
        cursor.close()
        return False
    else:
        log.info(f"Get leave status with return {True}, with function name {get_leave_status.__name__}")
        cursor.close()
        return True

def leave(id, user_id, dur, username, start_date, con):
    cursor = con.cursor()
    query = f"INSERT INTO mentorku.approval (id, userid, username, duration, start_dt, timestamp, status) Values (%s, %s, %s, %s, %s, now(), 2)"
    val = (id ,user_id, username ,int(dur), start_date)
    cursor.execute(query, val)
    con.commit()
    cursor.close()
    log.info(f"User inserted data into database with row count: {cursor.rowcount}, with function name {leave.__name__}")
    return True

def set_user_time(username, in_dt, con):
    cursor = con.cursor()
    query =f"""SELECT in_dt FROM mentorku.userlist where username = "{username}";"""
    cursor.execute(query)
    data = cursor.fetchall()
    
    if not data:
        log.info(f"No data write, function name {set_user_time.__name__} with return 409")
        cursor.close()
        return 409
    else:
        query = f"""UPDATE mentorku.userlist SET in_dt = %s WHERE username = %s"""
        val = (in_dt,username)
        cursor.execute(query, val)
        con.commit()
        log.info(f"User updated into database with row count: {cursor.rowcount}, function name {set_user_time.__name__} with return 200")
        cursor.close()
        return 200
    
def set_passwd(password, user_id, con):
    cursor = con.cursor()
    query = f"""UPDATE mentorku.userlist SET passwd = %s WHERE userid = %s"""
    val = (password, user_id)
    cursor.execute(query, val)
    con.commit()
    cursor.close()
    log.info(f"User updated into database with row count: {cursor.rowcount}, function name {set_passwd.__name__} with return 200")
    return 200

def get_approval(con, username=None):
    cursor = con.cursor()
    if(username == "" or username is None):
        query = f"""SELECT id, username, duration, start_dt FROM mentorku.approval WHERE status = 2"""
        cursor.execute(query)
    elif (username != "" or username is not None):
        query =  f"""SELECT id, username, duration, start_dt FROM mentorku.approval WHERE status = 2 and username = %s"""
        val = (username,)
        cursor.execute(query, val)

    log.info(f"Return data from database with rowcount: {cursor.rowcount}, from function name {get_approval.__name__}")
    return cursor

def check_args(args):
    if(args):
        if(("" in args[0:]) or (None in args[0:])):
            log.info(f"Checked arguments returned {True} from function name {check_args.__name__}")
            return True
        else:
            log.info(f"Checked arguments returned {False} from function name {check_args.__name__}")
            return False
    else:
        log.info(f"Checked arguments returned {True} from function name {check_args.__name__}")
        return True
    
def set_room(room_id, room_name, room_type, con):
    cursor = con.cursor()
    query = f"""INSERT IGNORE INTO mentorku.room (room_id, room_name, timestamp, room_type ) VALUES (%s, %s, now(), %s)"""
    val = (room_id, room_name, room_type)
    cursor.execute(query, val)
    con.commit()
    cursor.close()
    log.info(f"Succesfully recorded room info to database, returned {200}, from function name {set_room.__name__}")
    return 200

def get_channelid(con, room_name=None):
    cursor = con.cursor()
    if(room_name is not None):
        query = f"SELECT room_id FROM mentorku.room WHERE room_type='channel' and room_name=%s"
        val = (room_name,)
        cursor.execute(query, val)
        res = cursor.fetchone()
        cursor.close()
        return res[0]
    else:
        query = f"SELECT room_id FROM mentorku.room WHERE room_type='channel' and room_name=%s"
        val = (room_name,)
        cursor.execute(query, val)
        res = cursor.fetchone()
        cursor.close()
        return res[0]
    
def set_approval(id, status, con):
    cursor = con.cursor()
    query = "UPDATE mentorku.approval SET status = %s WHERE id = %s and status = 2"
    val = (status, id)
    cursor.execute(query, val)
    cursor.commit()
    cursor.close()
    return 200