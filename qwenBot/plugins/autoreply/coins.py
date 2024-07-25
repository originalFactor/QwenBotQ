from nonebot import on_command
from nonebot.rule import to_me
from sqlite3 import connect
from datetime import datetime

conn = connect('coins.db')
cursor = conn.cursor()

cursor.executescript('''
CREATE TABLE IF NOT EXISTS coins (
    ID INT PRIMARY KEY NOT NULL,
    COIN INT DEFAULT 0 NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS uid ON coins (ID);
''')

dailySign = on_command("sign", to_me())
@dailySign.handle()
async def dailySignHandler():
    #cursor.execute()
    await dailySign.finish("Feature not yet implemented.")