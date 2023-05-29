import os
import telebot
from dotenv import load_dotenv 
import connector as db
import inject as qry
import datetime
import tzlocal
import prettytable as table
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
    qry.sign_in(id_chat=user_id_chat, msg_id=message_id, chat_tm=times, con=conn)
    times_delta = datetime.timedelta(hours=times.hour, minutes=times.minute, seconds=times.second)
    if(times_delta > sign_in_time):
        bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, but you're late for {times_delta - sign_in_time}")
    else:
        bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, you're on time")
    # try:
    #     qry.sign_in(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time, con=conn)
    #     sign_in_time = qry.get_time(id_chat=user_id_chat, con=conn)
    #     times = datetime.datetime.fromtimestamp(chat_time, local_timezone)
    #     if(times > sign_in_time):
    #         bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, but you're late for {times - sign_in_time}")
    #     else:
    #         bot.reply_to(message, f"{message.from_user.full_name} sign in at {times}. Sign in succesfully, you're on time")
    # except:
    #     bot.reply_to(message, "Failed to sign in !")
    #     print("failed to insert to database !")


@bot.message_handler(commands=['out'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    message_id = message.message_id
    chat_time = message.date
    try:
        qry.sign_out(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time, con=conn)
        get_time = get_time(id_chat=user_id_chat, con=conn)
        bot.reply_to(message, f"{message.from_user.full_name} out at {datetime.datetime.fromtimestamp(chat_time, local_timezone)}. Sign out succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")

@bot.message_handler(commands=['init','start'])
def init(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    member = bot.get_chat_member(user_id=user_id, chat_id=chat_id)
    username = member.user.username
    status = member.status
    ret = qry.init_data(user_id = user_id, username = username, admin_status=status, con=conn)
    if (ret == 200):
        bot.reply_to(message, f"Added new member to database, with name {message.from_user.full_name} at {datetime.datetime.fromtimestamp(message.date, local_timezone)}")
    elif (ret == 409):
        bot.reply_to(message, f"Duplicate user ! For {username}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, f"""This is an attendance bot, usage:\n\t\'in Sign in\n\t\'out Sign out \n\t\'help to display this message""")

@bot.message_handler(commands=['get_data_today'])
def get_data(message):
    user_id = message.from_user.id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        data = qry.get_data_today(con=conn)
        result = table.from_db_cursor(data)
        bot.reply_to(message, result.get_string())
    else:
        bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")

if __name__ == "__main__":
    bot.infinity_polling()