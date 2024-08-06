from datetime import datetime, timedelta

async def stillVaild(date:datetime)->bool:
    return date >= datetime.now()-timedelta(1)