import os
import re
import telebot
import datetime
import pytz
import asyncio
import mysql.connector as mysql
import logging as log
import connector as db
import inject as qry
import prettytable as table
from telebot import asyncio_filters
from dateutil.relativedelta import *
from dotenv import load_dotenv 
from telebot.async_telebot import AsyncTeleBot
from telebot.async_telebot import types
from telebot.async_telebot import util
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup

class passwdState(StatesGroup):
    passwd = State()
    user_id = State()

load_dotenv()
log.basicConfig(filename='mentorku.log', filemode='a', format='%(levelname)s - %(asctime)s - %(message)s', datefmt='%a, %d/%m/%Y %H:%M:%S', level=log.DEBUG)
log.info("Log started")

token = ''.join(os.environ.get("BOT_TOKEN_DEVEL"))
#token = ''.join(os.environ.get("BOT_TOKEN_PROD"))
conn = db.db_connect()
log.info('Database is connected')

bot = AsyncTeleBot(token)
log.info("bot succesfully connected")

local_timezone = pytz.timezone('Asia/Jakarta')
log.info(f"local timezone set at {local_timezone}")

qry.set_var(con=conn, tz = local_timezone)
log.info('Database variable had been set')

@bot.message_handler(commands=['in'])
async def signin(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    room_type = message.chat.type
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknown chat room")
    else:
        log.info("User called in from a group chat")
        ret_usrlist = qry.check_userlist_empty(id_chat=user_id_chat,con=conn)
        ret_onleave = qry.check_onleave(id_chat=user_id_chat, con = conn)
        if((ret_usrlist == 200)):
            if((ret_onleave == 404)):
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
            else:
                await bot.reply_to(message, "You are on leave, you cannot sign in")
        else:
            await bot.reply_to(message, "User list table were empty please run `/init` first")
            log.info(f"Failed to sign in, with name {message.from_user.full_name}")


@bot.message_handler(commands=['out'])
async def signin(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    room_type = message.chat.type

    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknow chat room")
    else:
        log.info("User called in from a group chat")
        ret_usrlist = qry.check_userlist_empty(id_chat=user_id_chat,con=conn)
        ret_onleave = qry.check_onleave(id_chat=user_id_chat, con = conn)
        if(ret_usrlist == 200):
            if(ret_onleave == 404):
                try:
                    ret = qry.sign_out(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
                    if(ret == 200):
                        await bot.reply_to(message, f"{message.from_user.full_name} out at {times}. Sign out succesfully.")
                        log.info(f"User sign out, with name {message.from_user.full_name}")
                    else:
                        await bot.reply_to(message, f"You didn't sign in today please run `/in` before you sign out.")
                        log.info(f"User failed to sign out due it didn't sign in !")
                except Exception as e:
                    await bot.reply_to(message, "Failed to sign out !")
                    log.error(repr(e))
            else:
                await bot.reply_to(message, "You are on leave, you cannot sign out")
        else:
            await bot.reply_to(message, "User list table were empty please run `/init` first !")
            log.info(f"Failed to sign out, with name {message.from_user.full_name}")

@bot.message_handler(commands=['init','start'])
async def init(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    room_type = message.chat.type
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknown chat room")
    else:
        log.info("User called in from a group chat")
        member = await bot.get_chat_member(user_id=user_id, chat_id=chat_id)
        log.info("Get get chat member")
        username = member.user.username
        names = message.from_user.full_name
        status = member.status
        if(username != "" or username is not None):
            ret = qry.init_data(user_id = user_id, username = username, admin_status=status, real_name= names, chat_id = chat_id, con=conn)
        else:
            await bot.reply_to(message, f"User didn't set thier telegram username ! Please set the username before run this command !")

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
/out: Sign out, if user didn't sign in the same day, that user cannot sign out.
/help: Will show this exact message.
/get_data {args}: Will sent attendence report based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data 1d`, `/get_data 7d`, `/get_data 1m`, or `/get_data 1y`.
/get_data_excel {args}: Will sent attendence report in Excel format based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data_excel 1d`, `/get_data_excel 7d`, `/get_data_excel 1m`, or `/get_data_excel 1y`.
/sick: Sick leave.
/leave {args}: On leave status, it is require how many days the user wanted to take its leave. (Max: 3 days and didn't take any leave within one month span).
E.g: `/leave 2d`
/set_in_time {args0} {args1}: Will set user's sign in time, this will determine if the user late or on time. it's required telegram username and sign in time with format hh:mm:ss.
E.g: `/set_in_time telegram_username 08:00:00`""")
    log.info("Successfuly displaying help")

@bot.message_handler(commands=['get_data'])
async def get_data_day(message):
    user_id = message.from_user.id
    room_type = message.chat.type

    if(room_type == "private"):
        admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
        log.info("Get admin stat")
        if(message.text != "" or message.text is not None):
            try:
                args = message.text.split()[1:]
            except Exception as e:
                await bot.reply_to(message, "Did you give any arguments ? get_data_excel <duration>\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
                log.error(f"Empty args. {repr(e)}")
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
                data.close()
                log.info(f"Print result data for {args[0]}")
            else:
                await bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
                log.error(f"Failed to print result data for {args[0]}")
        else:
            await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
            log.error(f"Wrong permission")
    else:
        await bot.reply_to(message, f"You call this command either from a group, or channel")

@bot.message_handler(commands=['get_data_excel'])
async def get_data_excel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id
    room_type = message.chat.type

    if(room_type == "private"):
        admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
        
        if(message.text != "" or message.text is not None):
            try:
                args = message.text.split()[1:]
            except Exception as e:
                await bot.reply_to(message, "Did you give any arguments ? get_data_excel <duration>\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
                log.error(f"Empty args. {repr(e)}")
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
    else:
        await bot.reply_to(message, f"You call this command either from a group, or channel")

@bot.message_handler(commands=['sick'])
async def sick_attendence(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    room_type = message.chat.type
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknow chat room")
    else:
        log.info("User called in from a group chat")
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
    room_type = message.chat.type
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknow chat room")
    else:
        log.info("User called in from a group chat")
        if(message.text != "" or message.text is not None):
            try:
                args = message.text.split()[1:]
            except Exception as e:
                await bot.reply_to(message, "Did you give any arguments ? leave <1-3>d")
                log.error(f"Empty args. {repr(e)}")
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
    user_id = message.from_user.id
    room_type = message.chat.type

    ret_usrlist = qry.check_userlist_empty(id_chat=user_id,con=conn)
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from an appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from an appropiate group")
        log.warning("User called in from unknow chat room")
    else:
        log.info("User called in from a group chat")
        admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
        if(admin_stat):
            if(ret_usrlist == 200):
                if(message.text != "" or message.text is not None):
                    try:
                        args = message.text.split()[1:3]
                    except Exception as e:
                        await bot.reply_to(message, "Did you give any arguments ? set_in_time <username> <time hh:mm::ss>")
                        log.error(f"Empty args. {repr(e)}")
                else:
                    await bot.reply_to(message, "Did you give what time the user should sign in ? Format: hh:mm:ss")
                    log.error(f"Wrong format or Null, input get {message.text}")
                times = ''.join(args[1])
                username = ''.join(args[0])
                if(username != "" or username is not None):
                    if(re.search("[0-9][0-9]:[0-9][0-9]:[0-9][0-9]", times)):
                        ret = qry.set_user_time(username=username, in_dt=times, con=conn)
                        if(ret == 200):
                            await bot.reply_to(message, f"""Succesfully change in time for user {username} at {times}""")
                            log.info(f"Successfuly changed {username} at time {times}")
                    else:
                        await bot.reply_to(message, f"Invalid format ! Format: hh:mm:ss\nE.g: 08:30:00")
                        log.error("Invalid format")
                else:
                    await bot.reply_to(message, f"User didn't set thiers username, please set thier username !")
                    log.warning("User didn't have any valid username")
            else:
                await bot.reply_to(message, f"User list table were empty please run `/init` first !")
                log.warning("User not found in userlist table !")
        else:
            await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
            log.error("Wrong permission !")

@bot.message_handler(commands=['set_password'])
async def set_passwd(message):
    room_type = message.chat.type

    if(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from an appropiate group ")
    elif(room_type == "private" or room_type == "group"):
        await bot.set_state(message.from_user.id, passwdState.passwd, message.chat.id)
        await bot.set_state(message.from_user.id, passwdState.user_id, message.chat.id)
        await bot.send_message(message.chat.id, f"Please enter your password (It's must containts 8 characters)", reply_markup=types.ForceReply(selective=False))

@bot.message_handler(commands=['cancel'], state="*")
async def cancel_state(message):
    await bot.send_message(message.chat.id, f"Command canceled !")
    await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=passwdState.passwd)
async def store_data(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as passwd:
        passwd['passwd'] = message.text
        passwd['user_id'] = message.from_user.id
    
    ret = qry.set_passwd(password=passwd['passwd'], user_id=passwd['user_id'], con=conn)

    if(ret == 200):
        await bot.send_message(message.chat.id, f"Password successfully been set")
    else:
        await bot.send_message(message.chat.id, f"Password couldn't be set")


@bot.message_handler(commands=['get_log'])
async def get_log(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        num_newlines = 0
        with open("mentorku.log", 'r') as logs:
            try:
                logs.seek(-2, os.SEEK_END)    
                while num_newlines < 5:
                    logs.seek(-2, os.SEEK_CUR)
                    if logs.read(1) == b'\n':
                        num_newlines += 1
            except OSError:
                logs.seek(0)
            last_line = logs.readlines()

        split_txt = util.smart_split(last_line, chars_per_string=1500)
        
        print(split_txt)

        for txt in split_txt:
            await bot.send_message(chat_id, txt)

        log.info(f"Sent logs info for {message.from_user.full_name}")
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error("Wrong permission !")

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

async def main():
    await asyncio.gather(bot.infinity_polling())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        log.error(repr(e))
        conn.close()
        log.info("Closing database")
        log.warning("Program shutdown")