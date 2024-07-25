from nonebot import on_command
from nonebot.rule import to_me
from sqlite3 import connect
from datetime import datetime

conn = connect('coins.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF EXISTS(
    ID INT PRIMARY KEY NOT NULL,
    COIN INT DEFAULT 0 NOT NULL
)
''')

dailySign = on_command("sign", to_me())
@dailySign.handle()
async def dailySignHandler():
    cursor.execute()

