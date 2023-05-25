import os
import telebot
from dotenv import load_dotenv 
import connector as db
import inject as qry
import datetime
import tzlocal
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
    user_real_name = message.from_user.first_name + ' ' + message.from_user.last_name
    message_id = message.message_id
    chat_time = message.date
    try:
        # qry.sign_in(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time)
        bot.reply_to(message, f"{user_real_name} sign in at {datetime.datetime.fromtimestamp(chat_time, local_timezone)}. Sign in succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")

@bot.message_handler(commands=['out'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.username
    user_real_name = message.from_user.first_name + ' ' + message.from_user.last_name
    message_id = message.message_id
    chat_time = message.date
    try:
        # qry.sign_out(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time)
        bot.reply_to(message, f"{user_real_name} out at {datetime.datetime.fromtimestamp(chat_time, local_timezone)}. Sign out succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")

@bot.message_handler(commands=['init'])
def init(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    member = bot.get_chat_member(user_id=user_id, chat_id=chat_id)
    bot.reply_to(message, f"{member}")
    print (member)

if __name__ == "__main__":
    bot.infinity_polling()