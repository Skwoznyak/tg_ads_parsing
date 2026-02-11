# (.venv) PS C:\Users\secre\OneDrive\Рабочий стол\max_dodep> uvicorn fast_pars.main:app --reload запускал

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

import os
import sys

# Каталог, где лежит этот файл (fast_pars)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Корень проекта (max_dodep) — родитель fast_pars
PROJECT_ROOT = os.path.dirname(BASE_DIR)

from routers.parsing_router import parsing_router
from auth.auth import auth_router


from auth.auth_deps import security

import uvicorn

app = FastAPI(title="Telegram Ads Parser API")
security.handle_errors(app)


app.include_router(auth_router)
app.include_router(parsing_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
