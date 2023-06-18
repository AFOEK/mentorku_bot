import os
import re
import telebot
import datetime
import tzlocal
import asyncio
import logging as log
import aioschedule as schedule
import connector as db
import inject as qry
import prettytable as table
from dateutil.relativedelta import *
from dotenv import load_dotenv 
from telebot.async_telebot import AsyncTeleBot

load_dotenv()
log.basicConfig(filename='mentorku.log', filemode='a', format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%a, %d/%m/%Y %H:%M:%S', level=log.INFO)
log.propagate = False
log.info("Log started")

token = ''.join(os.environ.get("BOT_TOKEN"))
conn = db.db_connect()
log.info('Database is connected')

bot = AsyncTeleBot(token)
log.info("bot succesfully connected")

local_timezone = tzlocal.get_localzone()

@bot.message_handler(commands=['in'])
async def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    message_id = message.message_id
    chat_time = message.date
    sign_in_time = qry.get_time(id_chat=user_id_chat, con=conn)
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    times_delta = datetime.timedelta(hours=times.hour, minutes=times.minute, seconds=times.second)
    try:
        qry.sign_in(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
        if(times_delta > sign_in_time):
            await bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, but you're late for {times_delta - sign_in_time}")
        else:
            await bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, you're on time")
        log.info(f"User sign in, with name {message.from_user.full_name}")
    except Exception as e:
        await bot.reply_to(message, "Failed to sign in !")
        log.error(repr(e))


@bot.message_handler(commands=['out'])
async def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    try:
        qry.sign_out(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
        await bot.reply_to(message, f"{message.from_user.full_name} out at {times}. Sign out succesfully")
        log.info(f"User sign out, with name {message.from_user.full_name}")
    except Exception as e:
        await bot.reply_to(message, "Failed to sign out !")
        log.error(repr(e))

@bot.message_handler(commands=['init','start'])
async def init(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    member = await bot.get_chat_member(user_id=user_id, chat_id=chat_id)
    log.info("Get get chat member")
    username = member.user.username
    names = message.from_user.full_name
    status = member.status
    ret = qry.init_data(user_id = user_id, username = username, admin_status=status, real_name= names, chat_id = chat_id, con=conn)
    if (ret == 200):
        await bot.reply_to(message, f"Added new member to database, with name {names} at {datetime.datetime.fromtimestamp(message.date, local_timezone)}")
        log.info(f"Successfuly insert data into database, with user {names}")
    elif (ret == 204):
        await bot.reply_to(message, f"Successfuly update for {username}")
        log.info(f"Successfuly update data, with user {names}")
    else:
        await bot.reply_to(message, f"Failed to insert or update user ! For {username}")
        log.error(f"Failed to insert user, with user {names}")

@bot.message_handler(commands=['help'])
async def help(message):
    await bot.reply_to(message, """
/start or /init: Will read "user_name", "full_name", "user_id", and "member_status" of the user. This command just use once when new user joined to the group.
/in: Sign in, if user late it will give how many hours, minutes, and seconds the user already passed.
/out: Sign out.
/help: Will show this exact message.
/get_data {args}: Will sent attendence report based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data 1d`, `/get_data 7d`, `/get_data 1m`, or `/get_data 1y`.
/get_data_excel {args}: Will sent attendence report in Excel format based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data_excel 1d`, `/get_data_excel 7d`, `/get_data_excel 1m`, or `/get_data_excel 1y`.
/sick: Sick leave.
/leave {args}: On leave status, it is require how many days the user wanted to take its leave. (Max: 3 days and didn't take any leave within one month span).
E.g: `/leave 2d`
/set_in_time: Will set user's sign in time, this will determine if the user late or on time.""")
    log.info("Successfuly displaying help")

@bot.message_handler(commands=['get_data'])
async def get_data_day(message):
    user_id = message.from_user.id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    log.info("Get admin stat")
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        await bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
        log.error("Invalid args")

    if(admin_stat):
        try:
            data = qry.get_data(con=conn, args = args[0])
        except Exception as e:
            await bot.reply_to(message, "Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(repr(e))
        if(data != 409):
            result = table.from_db_cursor(data)
            await bot.reply_to(message, result)
            log.info(f"Print result data for {args[0]}")
        else:
            await bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(f"Failed to print result data for {args[0]}")
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error(f"Wrong permission")

@bot.message_handler(commands=['get_data_excel'])
async def get_data_excel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        await bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
        log.error("Invalid args")

    if(admin_stat):
        try:
            ret = qry.get_data_excel(con=conn, args = args[0])
        except Exception as e:
            await bot.reply_to(message, "Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(repr(e))

        if(ret != 409):
            await bot.send_document(chat_id=chat_id, document=telebot.types.InputFile('Mentorku attendance '+ ret +'.xlsx'), reply_to_message_id=msg_id)
            log.info(f"Sent message for {message.from_user.full_name}")
        else:
            await bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(f"Failed to print result data for {args[0]}")
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error(f"Wrong permission")

@bot.message_handler(commands=['sick'])
async def sick_attendence(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    try:
        qry.sick(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
        await bot.reply_to(message, f"{message.from_user.full_name} sick leave at {times}. Get well soon")
        log.info(f"Successfuly insert data, with user {message.from_user.full_name}")
    except:
        await bot.reply_to(message, "Failed to set sick leave !")
        log.error(f"failed to insert to database, with user {message.from_user.full_name}")

@bot.message_handler(commands=['leave'])
async def leave_attendence(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        await bot.reply_to(message, "Did you give how many days you want to take on leave ?")
        log.error("Invalid args")

    dur = ''.join(re.findall("[0-9]", args[0]))

    if(qry.get_leave_status(userid=user_id_chat, con=conn)):
        if(int(dur) >= 4):
            await bot.reply_to(message, "You can take 3 days leave only")
            log.error(f"Leave day exceded 3 days !, requested by {message.from_user.full_name}")
        else:
            ret = qry.leave(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, dur=dur, con=conn)

        if(ret):
            await bot.reply_to(message, "You requested leave for " + dur + " days")
        else:
            await bot.reply_to(message, "Did you give how many days you want to take on leave ?")
            log.error("Invalid args")
    else:
        await bot.reply_to(message, "You can take 3 days leave in ONE month, if any urgent matters please contact your supervisior !")
        log.error(f"Leave day exceded 3 days in 1 month !, requested by {message.from_user.full_name}")
    
@bot.message_handler(commands=['set_in_time'])
async def set_in_time(message):
    fullname = message.from_user.full_name
    user_id = message.from_user.id

    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        if(message.text != "" or message.text is not None):
            args = message.text.split()[1:3]
        else:
            await bot.reply_to(message, "Did you give what time the user should sign in ? Format: hh:mm:ss")
            log.error(f"Wrong format or Null, input get {message.text}")

        times = ''.join(args[1])
        username = ''.join(args[0])
        if(re.search("[0-9][0-9]:[0-9][0-9]:[0-9][0-9]", times)):
            ret = qry.set_user_time(username=username, in_dt=times, con=conn)
            if(ret == 200):
                await bot.reply_to(message, f"""Succesfully change in time for user {fullname}""")
                log.info(f"Successfuly changed {message.from_user.full_name} in time {times}")
        else:
            await bot.reply_to(message, f"Invalid format ! Format: hh:mm:ss\nE.g: 08:30:00")
            log.error("Invalid format")
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error("Wrong permission !")

async def schedule_jobs():
    in_dt = qry.check_in_dt(con = conn)
    recent_signin = qry.recent_signin(con = conn)
    try:
        if not recent_signin:
            for i in in_dt:
                time_now = datetime.datetime.now()
                times_delta_now = datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
                times = i[3]
                deltas = times_delta_now - times
                if(times <= times_delta_now):
                    await bot.send_message(chat_id=i[2], text = f"""<a href="tg://user?id={i[0]}]">{i[1]}</a>, your're going to late, please sign in ASAP. <b>You have {deltas} more !</b>""", parse_mode="HTML")
                    log.info(f"Sent reminder for username {i[1]}")
        else:
            for j in recent_signin:
                if(j[1] == i[1]):
                    pass
                else:
                    for i in in_dt:
                        time_now = datetime.datetime.now()
                        times_delta_now = datetime.timedelta(hours=time_now.hour, minutes=time_now.minute, seconds=time_now.second)
                        times = i[3]
                        deltas = times_delta_now - times
                        if(times <= times_delta_now):
                            await bot.send_message(chat_id=i[2], text = f"""<a href="tg://user?id={i[0]}]">{i[1]}</a>, your're going to late, please sign in ASAP. <b>You have {deltas} more !</b>""", parse_mode="HTML")
                            log.info(f"Sent reminder for username {i[1]}")
    except Exception as e:
        log.error(repr(e))

async def scheduler():
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(bot.infinity_polling(), scheduler())

if __name__ == "__main__":
    schedule.every().day.at("06:00").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("06:15").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("06:30").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("06:45").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("07:00").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("07:15").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("07:30").do(schedule_jobs)
    log.info("Schedule job fire")
    schedule.every().day.at("07:45").do(schedule_jobs)
    log.info("Schedule job fire")
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        log.error(repr(e))
        conn.close()
        log.info("Closing database")
        log.warning("Program shutdown")