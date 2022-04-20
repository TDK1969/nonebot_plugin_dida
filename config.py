from pydantic import BaseSettings

class Config(BaseSettings):
    # Your Config Here
    dida_phone: str
    dida_password: str
    dida_genid: bool = True
    class Config:
        extra = "ignore"