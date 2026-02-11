from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig

from pydantic import BaseModel

from auth.auth_deps import *


auth_router = APIRouter()


class UserLoginSchema(BaseModel):
    Api_key: str


@auth_router.post('/login', tags=['Авторизация в апи'])
def login(creds: UserLoginSchema, response: Response):
    if creds.Api_key == MY_API_KEY:
        token = security.create_access_token(uid='12345')
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {'message': 'Успешная авторизация', 'access_token': token}
    raise HTTPException(
        status_code=401, detail='Incorrect Api Key')