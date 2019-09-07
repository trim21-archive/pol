from pydantic import BaseModel

from app.services.bgm_tv.model import AuthResponse


class FinishAuth(BaseModel):
    api_key: str

    # class Config:
    #     schema_extra = {
    #         'example': [
    #             {'api_key': 'string'},
    #         ],
    #     }


class Me(AuthResponse):
    auth_time: int
