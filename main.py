import os
import random
import re
import string
import telebot
import datetime
import pytz
import asyncio
import hashlib
import logging as log
import connector as db
import inject as qry
import prettytable as table

from dotenv import load_dotenv 
from telebot import asyncio_filters
from dateutil.relativedelta import *
from dateutil.relativedelta import *
from telebot.async_telebot import AsyncTeleBot
from telebot.async_telebot import types
from telebot.asyncio_handler_backends import State, StatesGroup

class passwdState(StatesGroup):
    passwd = State()

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
    room_name = message.chat.title
    
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
            qry.set_room(room_id=chat_id, room_name=room_name, con=conn)
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
/leave {args0} {args1}: On leave status, it is require how many days and when the user wanted to take its leave. (Max: 3 days and didn't take any leave within one month span).
E.g: `/leave 2d 20/07/2023`, `/leave 3d 18/07/2023`
/set_in_time {args0} {args1}: Will set user's sign in time, this will determine if the user late or on time. it's required telegram username and sign in time with format hh:mm:ss.
E.g: `/set_in_time telegram_username 08:00:00`
/get_log: Will print out last 5 lines of logs.
/set_password: Will start series of command which user need to give his/her password""")
    log.info("Successfuly displaying help")

@bot.message_handler(commands=['get_data'])
async def get_data_day(message):
    user_id = message.from_user.id
    room_type = message.chat.type

    if(room_type == "private"):
        admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
        log.info("Get admin stat")
        
        try:
            args = message.text.split()[1:]
        except Exception as e:
            await bot.reply_to(message, "Did you give any arguments ? get_data_excel <duration>\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(f"Invalid args. {repr(e)}")

        if(qry.check_args(args)):
            args = ["now"]
            log.info(f"Empty argument fallback to `now` selection")

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

        try:
            args = message.text.split()[1:]
        except Exception as e:
            await bot.reply_to(message, "Did you give any arguments ? get_data_excel <duration>\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
            log.error(f"Invalid args. {repr(e)}")

        if(qry.check_args(args)):
            args = ["now"]
            log.info(f"Empty argument fallback to `now` selection")

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
    username = message.from_user.username
    room_type = message.chat.type
    
    if(room_type == "private"):
        await bot.reply_to(message, "You called this bot from your personal chat room, please call it from appropiate group")
        log.warning("User called in from personal chat room")
    elif(room_type == "supergroup" and room_type == "channel"):
        await bot.reply_to(message, "You called this bot from unknown chat room, please call it from appropiate group")
        log.warning("User called in from unknow chat room")
    else:
        log.info("User called in from a group chat")

        try:
            args = message.text.split()[1:3]
        except Exception as e:
            await bot.reply_to(message, "Did you give any arguments ? leave <1-3>d")
            log.error(f"Invalid args. {repr(e)}")
            return
        
        if(qry.check_args(args)):
            await bot.reply_to(message, "Did you give how many days you want to take on leave ?")
            log.error("Invalid args")
            return

        dur = ''.join(re.findall("[0-9]", args[0]))
        dt = ''.join(re.findall(r"\b\d{2}/\d{2}/\d{4}\b", args[1]))
        days = datetime.datetime.strptime(dt,"%d/%m/%Y")

        if(qry.get_leave_status(userid=user_id_chat, con=conn)):
            if(int(dur) >= 4):
                await bot.reply_to(message, "You can take 3 days leave only")
                log.error(f"Leave day exceded 3 days !, requested by {message.from_user.full_name}")
            else:
                diff = abs((datetime.datetime.now().date() - days.date()).days)
                if(diff >= 3):
                    temp_id = str(message.from_user.username) + str(message.from_user.id) + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
                    id_str = hashlib.sha512(temp_id.encode()).hexdigest()
                    ret = qry.leave(id=id_str[:15], user_id=user_id_chat, username=username, dur=dur, start_date=days, con=conn)
                    log.info(f"User on leave, with name {message.from_user.full_name}")
                    if(ret):
                        new_date = days + relativedelta(days=+int(dur))
                        await bot.reply_to(message, f"You requested leave for {dur} days, from {days.date()} until {new_date.date()}, already has been recorded please wait for approval by your supervisor")
                    else:
                        await bot.reply_to(message, "Did you give how many days you want to take on leave ?")
                        log.error("Invalid args")
                else:
                    await bot.reply_to(message, f"You need to request on leave H-3 before, but you requested at {diff}")
                    log.warning(f"User requested leave at {diff} ! with username {message.from_user.full_name}.")
        else:
            await bot.reply_to(message, "You can take 3 days leave in ONE month, if any urgent matters please contact your supervisor !")
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
                try:
                    args = message.text.split()[1:3]
                except Exception as e:
                    await bot.reply_to(message, "Did you give any arguments ? set_in_time <username> <time hh:mm::ss>")
                    log.error(f"Invalid args. {repr(e)}")
                    return

                if(qry.check_args(args)):
                    await bot.reply_to(message, "Did you give what time the user should sign in ? Format: hh:mm:ss")
                    log.error(f"Wrong format or Null, input get {message.text}")
                    return
                
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
    user_id = message.from_user.id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        if(room_type == "supergroup" and room_type == "channel"):
            await bot.reply_to(message, "You called this bot from unknown chat room, please call it from an appropiate group ")
            log.error("User called from inside a channel or supergroup")
        elif(room_type == "private" or room_type == "group"):
            log.info("User called from inside a group")
            await bot.set_state(message.from_user.id, passwdState.passwd, message.chat.id)
            await bot.send_message(message.chat.id, f"Please enter your password (It's must containts 8 characters)", reply_markup=types.ForceReply(selective=False))
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        await bot.delete_state(message.from_user.id, message.chat.id)
        log.error("Wrong permission !")

@bot.message_handler(commands=['cancel'], state="*")
async def cancel_state(message):
    log.info("User cancel the operation")
    await bot.send_message(message.chat.id, f"Command canceled !")
    await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(state=passwdState.passwd)
async def store_data(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as passwd:
        passwd['passwd'] = message.text
    
    log.info("Get user password string from state")
    passwd_salted = passwd['passwd'] + str(message.from_user.id)
    hashed_passwd = hashlib.md5(passwd_salted.encode())
    log.info("Salted user's password")
    ret = qry.set_passwd(password=hashed_passwd, user_id=message.from_user.id, con=conn)

    if(ret == 200):
        await bot.send_message(message.chat.id, f"Password successfully been set")
        await bot.delete_state(message.from_user.id, message.chat.id)
    else:
        await bot.send_message(message.chat.id, f"Password couldn't be set")
        await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(commands=['get_log'])
async def get_log(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        log.info("Opening log file")
        try:
            with open('mentorku.log', 'r', encoding='utf-8') as file:
                text = file.readlines()[-10:]

            chunk_size = 4
            line_chunks = [text[i:i+chunk_size] for i in range (0, len(text), chunk_size)]

            for chunk in line_chunks:
                msg_txt = "".join(chunk)
                await bot.reply_to(message,msg_txt)
        except Exception as e:
            log.error(f"Invalid args. {repr(e)}")
        log.info(f"Sent logs info for {message.from_user.full_name}")
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error("Wrong permission !")

@bot.message_handler(commands=['get_approval'])
async def set_approval(message):
    user_id = message.from_user.id
    room_type = message.chat.type

    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        if(room_type == "supergroup" and room_type == "channel"):
            await bot.reply_to(message, "You called this bot from unknown chat room, please call it from an appropiate group ")
            log.error("User called from inside a channel or supergroup")
        elif(room_type == "private" or room_type == "group"):
            log.info("User called from inside a group/private room")

            try:
                args = message.text.split()[1:]
            except Exception as e:
                await bot.reply_to(message, "Did you give username who you want approv their leave ? Displaying all pending approval\nUsage: approval <username>")
                log.error(f"Invalid args. {repr(e)}")
                return

            if(not qry.check_args(args)):    
                ret = qry.get_approval(con=conn, username=args[0])
            else:
                ret = qry.get_approval(con=conn)

            result = table.from_db_cursor(ret)
            await bot.reply_to(message, result)
            ret.close()
    else:
        await bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")
        log.error("Wrong permission !")

@bot.channel_post_handler(commands=["init_room"])
async def init_channel(message):
    room_type = message.chat.type
    room_name = message.chat.title
    chat_id = message.chat.id

    if(message.from_user is None):
        if(room_type == "channel"):
            ret = qry.set_room(room_id=chat_id, room_type=room_type, room_name=room_name, con=conn)
            if(ret == 200):
                await bot.delete_message(message_id=message.message_id, chat_id=chat_id)
                await bot.reply_to(message, f"Room have been set !")
                log.info("Room info has been set")
            else:
                bot.reply_to(message, "Failed to setup room info")
                log.error("Error when setup room info")
        else:
            await bot.reply_to(message, "You called this bot from group or private chat. Please call it from an appropiate group ")
            log.error("User called from inside a group or private")
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