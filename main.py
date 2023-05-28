import os
import telebot
from dotenv import load_dotenv 
import connector as db
from telegram.ext import Updater, CommandHande
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
    try:
        # qry.sign_in(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time, con=conn)
        bot.reply_to(message, f"{message.user.full_name} sign in at {datetime.datetime.fromtimestamp(chat_time, local_timezone)}. Sign in succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")

@bot.message_handler(commands=['out'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    message_id = message.message_id
    chat_time = message.date
    try:
        # qry.sign_out(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time, con=conn)
        bot.reply_to(message, f"{message.user.full_name} out at {datetime.datetime.fromtimestamp(chat_time, local_timezone)}. Sign out succesfully")
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
    # ret = qry.init_data(user_id = user_id, username = username, status = status, con=conn)
    # if (ret == 200):
    #     bot.reply_to(message, f"Added new member to database, with name {message.user.full_name} at {datetime.datetime.fromtimestamp(message.date, local_timezone)}")
    #     print (member)
    # elif (ret == 409):
    #     bot.reply_to(message, f"Duplicate user ! For {username}")
    bot.reply_to(message, f"Added new member to database, with name {message.user.full_name} at {datetime.datetime.fromtimestamp(message.date, local_timezone)}")

@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, f"""This is an attendance bot, usage:\n\t\'in Sign in\n\t\'out Sign out \n\t\'help to display this message""")

@bot.message_handler(commands=['get_data_today'])
def get_data(message):
    user_id = message.from_user.id
    admin_stat = qry.get_admin_stat(userid=user_id, con=conn)
    if(admin_stat):
        data = qry.get_data_today(con=conn)
        result = table([""])
    else:
        bot.reply_to(message, f"Permission denied ! Are you an admin or owner ?")

if __name__ == "__main__":
    bot.infinity_polling()