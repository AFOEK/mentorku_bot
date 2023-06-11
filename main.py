import os
import re
import telebot
import datetime
import tzlocal
import connector as db
import inject as qry
import prettytable as table
from dotenv import load_dotenv 

load_dotenv()

token = ''.join(os.environ.get("BOT_TOKEN"))
conn = db.db_connect()
print("database succesfully connected")

bot = telebot.TeleBot(token)
print("bot succesfully connected")

local_timezone = tzlocal.get_localzone()

@bot.message_handler(commands=['in'])
def signin(message):
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
            bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, but you're late for {times_delta - sign_in_time}")
        else:
            bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, you're on time")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")


@bot.message_handler(commands=['out'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    try:
        qry.sign_out(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
        bot.reply_to(message, f"{message.from_user.full_name} out at {times}. Sign out succesfully")
    except:
        bot.reply_to(message, "Failed to sign out !")
        print("failed to insert to database !")

@bot.message_handler(commands=['init','start'])
def init(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    member = bot.get_chat_member(user_id=user_id, chat_id=chat_id)
    username = member.user.username
    names = message.from_user.full_name
    status = member.status
    ret = qry.init_data(user_id = user_id, username = username, admin_status=status, real_name= names, chat_id = chat_id, con=conn)
    if (ret == 200):
        bot.reply_to(message, f"Added new member to database, with name {names} at {datetime.datetime.fromtimestamp(message.date, local_timezone)}")
    elif (ret == 204):
        bot.reply_to(message, f"Successfuly update for {username}")
    else:
        bot.reply_to(message, f"Failed to insert or update user ! For {username}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, """
/start or /init: Will read "user_name", "full_name", "user_id", and "member_status" of the user. This command just use once when new user joined to the group.
/in: Sign in, if user late it will give how many hours, minutes, and seconds the user already passed.
/out: Sign out.
/help: Will show this exact message.
/get_data {args}: Will sent attendence report based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data 1d`, `/get_data 7d`, `/get_data 1m`, or `/get_data 1y`.
/get_data_excel {args}: Will sent attendence report in Excel format based how many days, months, or year the user supplied. Possible options are 1d, 7d, 30d, 1w, 1m, 12m, and 1y.
E.g: `/get_data_excel 1d`, `/get_data_excel 7d`, `/get_data_excel 1m`, or `/get_data_excel 1y`.""")

@bot.message_handler(commands=['get_data'])
def get_data_day(message):
    user_id = message.from_user.id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")

    if(admin_stat):
        try:
            data = qry.get_data(con=conn, args = args[0])
        except IndexError:
            bot.reply_to(message, "Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
        if(data != 409):
            result = table.from_db_cursor(data)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
    else:
        bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")

@bot.message_handler(commands=['get_data_excel'])
def get_data_excel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    msg_id = message.message_id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")

    if(admin_stat):
        try:
            ret = qry.get_data_excel(con=conn, args = args[0])
        except IndexError:
            bot.reply_to(message, "Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")

        if(ret != 409):
            bot.send_document(chat_id=chat_id, document=telebot.types.InputFile('Mentorku attendance '+ ret +'.xlsx'), reply_to_message_id=msg_id)
        else:
            bot.reply_to(message, f"Did you give how many days you want to pull ?\nPossible options: now, 1d, 7d, 30d, 1w, 1m, 12m, 1y")
    else:
        bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")

@bot.message_handler(commands=['sick'])
def sick_attendence(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    try:
        qry.sick(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
        bot.reply_to(message, f"{message.from_user.full_name} sick leave at {times}. Get well soon")
    except:
        bot.reply_to(message, "Failed to set sick leave !")
        print("failed to insert to database !")

@bot.message_handler(commands=['leave'])
def leave_attendence(message):
    user_id_chat = message.from_user.id
    message_id = message.message_id
    chat_time = message.date
    times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    if(message.text != "" or message.text is not None):
        args = message.text.split()[1:]
    else:
        bot.reply_to(message, "Did you give how many days you want to take on leave ?")

    dur = ''.join(re.findall("[0-9]", args[0]))

    if(qry.get_leave_status(userid=user_id_chat, con=conn)):
        if(int(dur) >= 4):
            bot.reply_to(message, "You can take 3 days leave only")
        else:
            ret = qry.leave(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, dur=dur, con=conn)

        if(ret):
            bot.reply_to(message, "You requested leave for " + dur + " days")
        else:
            bot.reply_to(message, "Did you give how many days you want to take on leave ?")
    else:
        bot.reply_to(message, "You can take 3 days leave in ONE month, if any urgent matters please contact your supervisior !")
    
@bot.message_handler(commands=['set_in_time'])
def set_in_time(message):
    fullname = message.from_user.full_name
    user_id = message.from_user.id

    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        if(message.text != "" or message.text is not None):
            args = message.text.split()[1:3]
        else:
            bot.reply_to(message, "Did you give what time the user should sign in ? Format: hh:mm:ss")

        times = ''.join(args[1])
        username = ''.join(args[0])
        if(re.search("[0-9][0-9]:[0-9][0-9]:[0-9][0-9]", times)):
            ret = qry.set_user_time(username=username, in_dt=times, con=conn)
            if(ret == 200):
                bot.reply_to(message, f"""Succesfully change in time for user {fullname}""")
        else:
            bot.reply_to(message, f"Invalid format ! Format: hh:mm:ss\nE.g: 08:30:00")
    else:
        bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")


if __name__ == "__main__":
    bot.infinity_polling(timeout=50, long_polling_timeout=100)