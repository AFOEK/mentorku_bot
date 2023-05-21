import os
import telebot
from dotenv import load_dotenv 
import connector as db
load_dotenv()

token = ''.join(os.environ.get("BOT_TOKEN"))
conn = db.db_connect()

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['in'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.name
    message_id = message.message_id
    chat_time = message.date
    try:
        db.sign_in(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time)
        bot.reply_to(message, f"{user_name_chat} in at {chat_time}. Sign in succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")

@bot.message_handler(commands=['out'])
def signin(message):
    user_id_chat = message.from_user.id
    user_name_chat = message.from_user.name
    message_id = message.message_id
    chat_time = message.date
    try:
        db.sign_out(id_chat=user_id_chat, mgs_id=message_id, chat_tm=chat_time)
        bot.reply_to(message, f"{user_name_chat} out at {chat_time}. Sign out succesfully")
    except:
        bot.reply_to(message, "Failed to sign in !")
        print("failed to insert to database !")