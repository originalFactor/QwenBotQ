from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, field_validator
from httpx import AsyncClient
from . import config
from typing import Union, Dict

class User(BaseModel):
    id : str
    nick : str
    permission : int = 0
    system_prompt : str = config.system_prompt

    @property
    async def avatar(self)->bytes:
        return (await AsyncClient().get(f"http://q1.qlogo.cn/g?b=qq&nk={self.id}&s=100")).content

    @property
    async def couple(self)->Union[str,None]:
        cpData = await findCouple(self.id)
        if cpData:
            cp = Couple(**cpData)
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

database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]

users = database['users']

couples = database['couples']

async def isFirstTime():
    if not users.find_one({}):
        await users.insert_one(User(id=config.supermgr_id,nick='Undefined',permission=999).model_dump())
        await users.create_index('id', unique=True)
    if not couples.find_one({}):
        await couples.insert_one(Couple(A='0',B='0').model_dump())
        await users.create_index(['A','B'], unique=True)

async def getUser(id:str)->Union[User, None]:
    if user := await users.find_one({'id':id}):
        return User(**user)
    return None

async def createUser(user:User):
    await users.insert_one(user.model_dump())

async def updateUser(user:User):
    await users.update_one({'id':user.id},{'$set': user.model_dump()})

async def findCouple(x:str)->Union[Dict[str,str],None]:
    return await couples.find_one({'$or': [{'A': x}, {'B': x}]})

async def useCouple(a:str, b:str):
    if A := await findCouple(a):
        await couples.delete_one(A)
    if B := await findCouple(b):
        await couples.delete_one(B)
    await couples.insert_one(Couple(A=a,B=b).model_dump())