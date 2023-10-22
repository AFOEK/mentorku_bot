import mysql.connector
from dotenv import load_dotenv
import os
import logging as log
load_dotenv()

def db_connect():
    try:
        log.info("Connecting from local network")
        DB_ADD = os.environ.get("DB_ADD")
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_NAME = os.environ.get("DB_NAME")
        DB_PORT = os.environ.get("DB_PORT")

        db = mysql.connector.connect(
            host = ''.join(DB_ADD),
            user = ''.join(DB_USER),
            password = ''.join(DB_PASSWORD),
            database = ''.join(DB_NAME),
            port = ''.join(DB_PORT),
            pool_name = "Mentorku",
            pool_size = 5
        )
    except:
        log.info("Failed to connect from local network. Connecting using tunnel")
        DB_ADD_TUNNEL = os.environ.get("DB_ADD_TUNNEL")
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_NAME = os.environ.get("DB_NAME")
        DB_PORT_TUNNEL = os.environ.get("DB_PORT_TUNNEL")

        db = mysql.connector.connect(
            host = ''.join(DB_ADD_TUNNEL),
            user = ''.join(DB_USER),
            password = ''.join(DB_PASSWORD),
            database = ''.join(DB_NAME),
            port = ''.join(DB_PORT_TUNNEL),
            pool_name = "Mentorku",
            pool_size = 5
        )

    return db