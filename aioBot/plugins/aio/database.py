from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, field_validator
from httpx import AsyncClient
from . import config
from typing import Union, Dict
from datetime import datetime, timedelta

class User(BaseModel):
    id : str
    nick : str
    permission : int = 0
    system_prompt : str = config.system_prompt

    @property
    async def avatar(self)->bytes:
        return (await AsyncClient().get(f"http://q1.qlogo.cn/g?b=qq&nk={self.id}&s=640")).content

    @property
    async def couple(self)->Union[str,None]:
        if cp := await findCouple(self.id):
            return cp.B if cp.A==self.id else cp.A
        return None

    @field_validator('permission')
    @classmethod
    def validate_permission(cls, v:int)->int:
        if v>999: return 999
        if v<0: return 0
        return v

class Couple(BaseModel):
    A : str
    B : str
    date : datetime

database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]

users = database['users']

couples = database['couples']

async def isFirstTime():
    if users.find_one({}):
        await users.delete_many({})
        await users.drop_indexes()
    await users.insert_one(User(id=config.supermgr_id,nick='',permission=999).model_dump())
    await users.create_index('id', unique=True)
    if couples.find_one({}):
        await couples.delete_many({})
        await couples.drop_indexes()
    await couples.insert_one(Couple(A='0',B='0',date=datetime(2000,1,1)).model_dump())
    await couples.create_index(['A','B'], unique=True)

async def getUser(id:str)->Union[User, None]:
    if user := await users.find_one({'id':id}):
        return User(**user)
    return None

async def createUser(user:User):
    await users.insert_one(user.model_dump())

async def updateUser(user:User):
    await users.update_one({'id':user.id},{'$set': user.model_dump()})

async def findCoupleX(x:str)->Union[Couple,None]:
    tmp = await couples.find_one({'$or': [{'A': x}, {'B': x}]})
    return (Couple(**tmp) if tmp else None)

async def findCouple(x:str)->Union[Couple,None]:
    cp = await findCoupleX(x)
    return cp if cp and cp.date>=datetime.today()-timedelta(1) else None

async def useCouple(a:str, b:str):
    if A := await findCoupleX(a):
        await couples.delete_one(A.model_dump(exclude={'date'}))
    if B := await findCoupleX(b):
        await couples.delete_one(B.model_dump(exclude={'date'}))
    await couples.insert_one(Couple(A=a,B=b,date=datetime.now()).model_dump())
