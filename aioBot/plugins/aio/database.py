from motor.motor_asyncio import AsyncIOMotorClient
from . import config
from typing import Union, List
from .utils import *
from pydantic import BaseModel, field_validator
from httpx import AsyncClient
from os.path import isdir, split
from os import mkdir, listdir, remove
from nonebot import logger

class User(BaseModel):
    id : str
    nick : str
    permission : int = 0
    system_prompt : str = config.system_prompt
    coins : int = 0
    last_signed_date : datetime = datetime(1970,1,1)

    async def get_avatar_path(self)->Union[str,None]:
        if not isdir('cache'): mkdir('cache')
        base_dir = f'cache/{self.id}'
        if not isdir(base_dir): mkdir(base_dir)
        files = listdir(base_dir)
        return base_dir+'/'+files[0] if files else None
    
    @property
    async def avatar(self)->bytes:
        file = await self.get_avatar_path()
        if not file or not stillVaild(datetime.fromtimestamp(float(split(file)[1].split('.')[0]))):
            try:
                resp = await AsyncClient().get(f"http://q1.qlogo.cn/g?b=qq&nk={self.id}&s=640")
                if resp.status_code==200:
                    content = resp.content
                    if file: remove(file)
                    with open(f'cache/{self.id}/{int(datetime.now().timestamp())}.png', 'wb') as f:
                        f.write(content)
                    return content
                else:
                    logger.warning(
                        f'Avatar download failed because server returned an unexpected status code {resp.status_code}, '
                        'using the old one.'
                    )
            except Exception as e:
                logger.warning(f'Avartar download failed because client side network error, using the old one.')
        if file:
            with open(file, 'rb') as f:
                return f.read()
        return b''

    @property
    async def couple(self)->Union["Couple",None]:
        return await findCouple(self.id)
    
    @property
    async def sign_expire(self)->datetime:
        return self.last_signed_date+timedelta(1)

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

    async def opposite(self, me:str)->str:
        return self.A if self.B==me else self.B
    
    @property
    async def expire(self)->datetime:
        return self.date+timedelta(1)

database = AsyncIOMotorClient(config.mongo_uri)[config.mongo_db]

users = database['users']

couples = database['couples']

async def isFirstTime():
    if users.find_one({}):
        await users.delete_many({})
        await users.drop_indexes()
    await users.insert_many([User(id=_,nick='',permission=999).model_dump() for _ in config.supermgr_ids])
    await users.create_index('id', unique=True)
    if couples.find_one({}):
        await couples.delete_many({})
        await couples.drop_indexes()
    await couples.insert_one(Couple(A='0',B='0',date=datetime.fromtimestamp(0)).model_dump())
    await couples.create_index(['A','B'], unique=True)

async def getUser(id:str)->Union[User, None]:
    if user := await users.find_one({'id':id}):
        return User(**user)
    return None

async def createUser(user:User):
    await users.insert_one(user.model_dump())

async def updateUser(user:User):
    await users.update_one({'id':user.id},{'$set': user.model_dump()})

async def findCouple(x:Union[str,None], invaild:bool=False)->Union[Couple,None]:
    tmp = await couples.find_one({'$or': [{'A': x}, {'B': x}]})
    return Couple(**tmp) if tmp and (invaild or await stillVaild(tmp['date'])) else None

async def rmCouple(cp:Couple):
    await couples.delete_many(cp.model_dump(exclude={'date'}))

async def useCouple(cp:Couple):
    await rmCouple(cp)
    await couples.insert_one(cp.model_dump())

async def getTop10Users()->List[User]:
    result = []
    async for document in users.find({}).sort('coins',-1).limit(10):
        result.append(User(**document))
    return result
