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

from app.models import Role, UserProfile, Event
from django.contrib.auth.models import User
from SfeduEventBack.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

@router.get("/event/get-all-events")
def get_all_events():
    try:
        events = Event.objects.all()
        
        result = []

        for event in events:
            event_data = {
                "event_id": event.pk,
                "event_name": event.name,
                "event_description": event.description,
                "event_latitude": float(event.latitude),
                "event_longitude": float(event.longitude),
                "event_datetime": str(event.datetime_of_event),
                "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image.url}",
                "event_organizator_user_profile": {
                    "event_organizator_user_profile_id": event.organizator.pk,
                    "event_organizator_user_profile_role": {
                        "event_organizator_user_profile_role_id": event.organizator.role.pk,
                        "event_organizator_user_profile_role_name": event.organizator.role.name,
                        "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
                    },
                    "event_organizator_user": {
                        "event_organizator_user_id": event.organizator.user.pk,
                        "event_organizator_user_username": event.organizator.user.username,
                        "event_organizator_user_email": event.organizator.user.email,
                        "event_organizator_user_first_name": event.organizator.user.first_name,
                        "event_organizator_user_last_name": event.organizator.user.last_name
                    },
                },
            }
            result.append(event_data)

        return result

    except ValueError as e:
        # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

    except ObjectDoesNotExist as e:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Объектов нет: {str(e)}")

@router.get("/event/get-event")
def get_all_events(event_id: int):
    
    try:
        event = Event.objects.get(id=event_id)
        
        result = []
        event_data = {
            "event_id": event.pk,
            "event_name": event.name,
            "event_description": event.description,
            "event_latitude": float(event.latitude),
            "event_longitude": float(event.longitude),
            "event_datetime": str(event.datetime_of_event),
            "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image.url}",
            "event_organizator_user_profile": {
                "event_organizator_user_profile_id": event.organizator.pk,
                "event_organizator_user_profile_role": {
                    "event_organizator_user_profile_role_id": event.organizator.role.pk,
                    "event_organizator_user_profile_role_name": event.organizator.role.name,
                    "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
                },
                "event_organizator_user": {
                    "event_organizator_user_id": event.organizator.user.pk,
                    "event_organizator_user_username": event.organizator.user.username,
                    "event_organizator_user_email": event.organizator.user.email,
                    "event_organizator_user_first_name": event.organizator.user.first_name,
                    "event_organizator_user_last_name": event.organizator.user.last_name
                },
            },
        }
        result.append(event_data)

        return result
    
    except ValueError as e:
        # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

    except ObjectDoesNotExist as e:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Данный объект не существует: {str(e)}")


@router.post("/event/post-event")
def post_all_events(event: dict):
    
    try:
        # password: str, email: str, role: dict, first_name: str, last_name: str

        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите данные")

        name = event["name"]
        description = event["description"]
        latitude = float(event["latitude"])
        longitude = float(event["longitude"])
        # datetime = event["datetime"]
        image = event["image"]
        organizator_id = int(event["user_id"])

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Название не указано")

        if not latitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите широту")

        if not longitude:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите долготу")
            

        with transaction.atomic():
            event_created = Event.objects.create(
                name=name,
                description=description,
                latitude=latitude,
                longitude=longitude,
                image=image,
                organizator_id=organizator_id,
            )
            
            event_created.save()

            user_profile = UserProfile.objects.get(id=event_created.organizator.pk)

            return {
                "ok": True,
                "detail": f"Мероприятие успешно добавлено!",
                "data": {
                    "event_id": event_created.pk,
                    "event_name": event_created.name,
                    "event_description": event_created.description,
                    "event_latitude": float(event_created.latitude),
                    "event_longitude": float(event_created.longitude),
                    "event_datetime": str(event_created.datetime_of_event),
                    "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event_created.image.url}",
                    "event_organizator_user_profile": {
                        "event_organizator_user_profile_id": event_created.organizator.pk,
                        "event_organizator_user_profile_role": {
                            "event_organizator_user_profile_role_id": event_created.organizator.role.pk,
                            "event_organizator_user_profile_role_name": event_created.organizator.role.name,
                            "event_organizator_user_profile_role_is_can_post_event": event_created.organizator.role.is_can_post_event,
                        },
                        "event_organizator_user": {
                            "event_organizator_user_id": event_created.organizator.user.pk,
                            "event_organizator_user_username": event_created.organizator.user.username,
                            "event_organizator_user_email": event_created.organizator.user.email,
                            "event_organizator_user_first_name": event_created.organizator.user.first_name,
                            "event_organizator_user_last_name": event_created.organizator.user.last_name
                        },
                    },
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

    # except IntegrityError as e:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,
    #                         detail="Такой пользователь уже существует!")

    # except Role.DoesNotExist as e:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="Такой роли не существует!")

    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка: {e}")

    
    
    try:
        event = Event.objects.c(id=event_id)
        
        result = []
        event_data = {
            "event_id": event.pk,
            "event_name": event.name,
            "event_description": event.description,
            "event_latitude": float(event.latitude),
            "event_longitude": float(event.longitude),
            "event_datetime": str(event.datetime_of_event),
            "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image.url}",
            "event_organizator_user_profile": {
                "event_organizator_user_profile_id": event.organizator.pk,
                "event_organizator_user_profile_role": {
                    "event_organizator_user_profile_role_id": event.organizator.role.pk,
                    "event_organizator_user_profile_role_name": event.organizator.role.name,
                    "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
                },
                "event_organizator_user": {
                    "event_organizator_user_id": event.organizator.user.pk,
                    "event_organizator_user_username": event.organizator.user.username,
                    "event_organizator_user_email": event.organizator.user.email,
                    "event_organizator_user_first_name": event.organizator.user.first_name,
                    "event_organizator_user_last_name": event.organizator.user.last_name
                },
            },
        }
        result.append(event_data)

        return result
    
    except ValueError as e:
        # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

    except ObjectDoesNotExist as e:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Данный объект не существует: {str(e)}")

