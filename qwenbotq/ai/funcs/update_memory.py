from ...database import SessionMemory

UPDATE_MEMORY_PROMPT = {
    "type": "function",
    "function": {
        "name": "update_memory",
        "description": "如果有什么需要记下来的，可以拿小本本记下来（将全部替换）",
        "parameters": {
            "type": "object",
            "properties": {
                "new": {
                    "type": "string",
                    "description": "新的小本本内容",
                },
            },
            "required": ["new"],
        },
    },
}


async def update_memory(session_id: str, new: str) -> str:
    try:
        mem = await SessionMemory.get(session_id)
        if mem:
            await mem.set({SessionMemory.memory: new})
        else:
            mem = SessionMemory(id=session_id, memory=new)
            await mem.insert()
    except Exception as e:
        return f"小本本更新失败：{e}"
    return "成功更新小本本"


async def get_memory(session_id: str) -> str:
    try:
        mem = await SessionMemory.get(session_id)
        if not mem:
            mem = SessionMemory(id=session_id, memory='')
    except Exception as e:
        return f"小本本获取失败：{e}"
    return mem.memory