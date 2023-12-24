import os
from fastapi import APIRouter
from django.core.asgi import get_asgi_application
from fastapi import HTTPException
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from fastapi import HTTPException, status
from fastapi import Cookie, Depends, FastAPI, HTTPException, status, Response
from django.contrib.auth import login, logout, authenticate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt


router = APIRouter()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SfeduEventBack.settings")

django_app = get_asgi_application()

from app.models import Role, UserProfile
from django.contrib.auth.models import User
from SfeduEventBack.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str):
    username = username.split('@')[0].upper()
    user = authenticate(username=username, password=password)
    if user is not None:
        # Учетные данные верны, возвращаете True или объект пользователя
        return user
    else:
        # Учетные данные неверны
        return False

# Создание JWT


def create_token(data, secret_key):
    token = jwt.encode(data, secret_key, algorithm='HS256')
    return token

# Проверка JWT


def verify_token(token):
    try:
        secret_key = SECRET_KEY
        decoded_token = jwt.decode(token, secret_key, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"


# Функция для создания токена
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

# Конечная точка для генерации токена при успешной аутентификации
@router.post("/user/auth/token")
def login_for_access_token(form_data: UserLogin):
    try:
        if not authenticate_user(form_data.username, form_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный логин и/или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        true_username = form_data.username.split('@')[0].upper()
        user = User.objects.get(username=true_username)
        user_profile = UserProfile.objects.get(user__id=user.pk)
        
        user_profile_id = user_profile.pk
        access_token = create_access_token(
            data={
                "sub": int(user_profile_id)
            }, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин и/или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Профиль пользователя не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

class UserToken(BaseModel):
    auth_token: str

@router.post("/user/get-user-data")
def get_user_data(current_user: UserToken):
    try:
        auth_token = current_user.auth_token
        decoded_token_user_id = verify_token(auth_token)["sub"]
        if not auth_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Данного пользователя не существует.",
            )
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невалидные данные: {e}",
                headers={"WWW-Authenticate": "Bearer"},
            )

        
    try:
        user_profile = UserProfile.objects.get(id=decoded_token_user_id)
        return {
            "user_profile_id": user_profile.pk,   
            "user": {
                "user_id": user_profile.user.pk,
                "user_username": user_profile.user.username,
                "user_email": user_profile.user.email,
                "user_first_name": user_profile.user.first_name,
                "user_last_name": user_profile.user.last_name,
            },   
            "user_profile_role": {
                "user_profile_role_id": user_profile.role.pk,
                "user_profile_role_name": user_profile.role.name,
                "user_profile_role_is_can_post_event": user_profile.role.is_can_post_event
            }   
        }
    except UserProfile.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Такого пользователя не существует",
        )


# Пример защищенного эндпоинта
@router.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("user_profile_id")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"detail": f"Добро пожаловать, {username}!"}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удаётся валидировать данные",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/user/get-all-roles")
def get_all_roles():
    roles = Role.objects.all()

    result = []

    for role in roles:
        role_data = {
            "value": str(role.name),
            "label": str(role.name),
        }
        result.append(role_data)

    return result


@router.post("/user/post-new-user")
def post_new_user(user: dict):
    try:
        # password: str, email: str, role: dict, first_name: str, last_name: str

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите данные")

        first_name = user["firstName"]
        last_name = user["lastName"]
        password = user["password"]
        repeat_password = user["repeatPassword"]
        email = user["email"]
        role_name = user["role"]["select"]["value"]

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Почта не указана")

        if not email.endswith('@sfedu.ru'):
            raise ValidationError(
                'Неверный домен почты. Почта должна быть домена @sfedu.ru')

        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароль не указан")

        if password != repeat_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Пароли не совпадают")

        validate_password(password)  # Проверка пароля с помощью валидаторов

        username = email.split('@')[0].upper()
        print(username)

        with transaction.atomic():
            user_created = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )

            role = Role.objects.get(name=role_name)

            user_profile_created = UserProfile.objects.create(
                user=user_created,
                role=role
            )

            return {
                "ok": True,
                "detail": f"Регистрация успешна, {user_profile_created.user.first_name}",
                "data": {
                    "user_profile_role": {
                        "role_id": user_profile_created.role.pk,
                        "role_name": user_profile_created.role.name,
                        "role_is_can_post_event": user_profile_created.role.is_can_post_event,
                        "user": {
                            "user_id": user_created.pk,
                            "user_username": user_created.username,
                            "user_email": user_created.email,
                            "user_first_name": user_created.first_name,
                            "user_last_name": user_created.last_name,
                        }
                    }
                }
            }

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Ошибка валидации {', '.join(e.messages)}")

        # return {
        #     "ok": False,
        #     "status": 400,
        #     "error": f"Ошибка валидации: {', '.join(e.messages)}"
        # }

    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Такой пользователь уже существует!")

    except Role.DoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Такой роли не существует!")

    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка: {e}")


def get_current_user(token: str = Cookie(None)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходимо быть авторизованным пользователем.",
        )
    # Проверка и возврат пользователя по токену


def login_required(func):
    async def wrapper(*args, current_user=Depends(get_current_user), **kwargs):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Необходима аутентификация"
            )
        return await func(*args, **kwargs)
    return wrapper

# @router.post("/user/auth")
# def post_auth(login_data: dict):
#     email = login_data["email"]
#     password = login_data["password"]


# def authenticate_user(email: str, password: str):

#     if email == "user@example.com" and password == "password":
#         return {"email": email}
#     else:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")


@router.get("/private")
@login_required
def private_route():
    # Ресурс, доступный только после аутентификации
    return {"detail": "Это закрытый ресурс"}



@router.post("/user/logout")
def logout(response: Response):
    response.delete_cookie("token", path="/")
    response.delete_cookie("user_data", path="/")
    return {"detail": "Вы успешно вышли из системы"}
