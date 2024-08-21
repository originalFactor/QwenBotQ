# Copyright (C) 2024 originalFactor
# 
# This file is part of QwenBotQ.
# 
# QwenBotQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# QwenBotQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with QwenBotQ.  If not, see <https://www.gnu.org/licenses/>.

import fastapi, motor, dotenv, os, uvicorn

import motor.motor_asyncio

dotenv.load_dotenv()

app = fastapi.FastAPI()

dbConnection = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URI", 'mongodb://127.0.0.1:27017'))

couples = dbConnection[os.environ.get("MONGO_DB","aioBot")].couples

@app.get('/{qq}')
async def getCouple(qq:str)->str:
    if _ := await couples.find_one({'$or': [
        {'A': qq},
        {'B': qq}
    ]}):
        return _['A'] if _['B']==qq else _['B']
    return "null"

if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=8090)
