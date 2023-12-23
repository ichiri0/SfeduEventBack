from colorama import Fore, init
from fastapi import FastAPI
from routes.user import router as user_router
from routes.institute import router as insitute_router
from routes.event import router as event_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

init(autoreset=True)

# Цвет текста в консоли у логера
color_info = Fore.GREEN
color_error = Fore.RED

app.include_router(user_router)
app.include_router(insitute_router)
app.include_router(event_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Замените на нужный адрес React приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
