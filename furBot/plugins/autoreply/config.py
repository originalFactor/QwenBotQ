from pydantic import BaseModel, field_validator


class Config(BaseModel):
    """Plugin Config Here"""
    system_prompt : str = "You are a helpful assistant."
    dashscope_api_key : str

    @field_validator("dashscope_api_key")
    @classmethod
    def check_api_key(cls, v:str)->str:
        v = v.strip()
        if not v.startswith("sk-") or ' ' in v:
            raise ValueError("Please set a vaild dashscope api key.")
        return v
