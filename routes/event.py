import base64
import os
import shutil
from fastapi import APIRouter, File, UploadFile
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
from django.db.models import Q
import jwt

from fastapi import Query
from typing import Optional

from pydantic import BaseModel

router = APIRouter()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SfeduEventBack.settings")

django_app = get_asgi_application()

from app.models import EventCategory, Role, UserProfile, Event
from django.contrib.auth.models import User
from SfeduEventBack.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

# @router.get("/event/get-all-events")
# def get_all_events():
#     try:
#         events = Event.objects.all()
        
#         result = []

#         for event in events:
#             event_data = {
#                 "event_id": event.pk,
#                 "event_name": event.name,
#                 "event_description": event.description,
#                 "event_latitude": float(event.latitude),
#                 "event_longitude": float(event.longitude),
#                 "event_datetime": str(event.datetime_of_event),
#                 "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image.url}",
#                 "event_organizator_user_profile": {
#                     "event_organizator_user_profile_id": event.organizator.pk,
#                     "event_organizator_user_profile_role": {
#                         "event_organizator_user_profile_role_id": event.organizator.role.pk,
#                         "event_organizator_user_profile_role_name": event.organizator.role.name,
#                         "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
#                     },
#                     "event_organizator_user": {
#                         "event_organizator_user_id": event.organizator.user.pk,
#                         "event_organizator_user_username": event.organizator.user.username,
#                         "event_organizator_user_email": event.organizator.user.email,
#                         "event_organizator_user_first_name": event.organizator.user.first_name,
#                         "event_organizator_user_last_name": event.organizator.user.last_name
#                     },
#                 },
#             }
#             result.append(event_data)

#         return result

#     except ValueError as e:
#         # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
#         raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

#     except ObjectDoesNotExist as e:
#         raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail=f"Объектов нет: {str(e)}")




@router.get("/event/get-all-events")
# @router.post("/event/get-all-events")
def get_all_events(search_text: Optional[str] = None, date_start: Optional[str] = None, date_end: Optional[str] = None, event_category: Optional[dict] = None):
    try:
        # if filter_data:
        #     search_text = filter_data.get("search_text")
        #     date_start = filter_data.get("date_start")
        #     date_end = filter_data.get("date_end")
        #     event_category = filter_data.get("event_category")
        
        # Создание динамического фильтра на основе переданных данных
        filters = Q()

        if search_text:
            filters &= Q(name__icontains=search_text) | Q(description__icontains=search_text)
        if date_start:
            filters &= Q(datetime_start__gte=date_start)
        if date_end:
            filters &= Q(datetime_start__lte=date_end)
        if event_category:
            print(event_category)
            event_category = event_category["newCategory"]["value"]
            filters &= Q(event_category__name=event_category)
        
        # Применение фильтров к запросу
        events = Event.objects.filter(filters)
        
        result = []

        for event in events:
            event_data = {
                "event_id": event.pk,
                "event_name": event.name,
                "event_description": event.description,
                "event_address": event.address,
                "event_start": event.datetime_start,
                "event_end": event.datetime_end,
                "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app/media{event.image.url.split('media')[-1]}",
                "event_category": {
                        "event_category_id": event.event_category.pk,
                        "event_category_name": event.event_category.name,
                        "event_category_color": event.event_category.color_hex,
                        },
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
        # Обработка ошибок преобразования типов данных или других исключений
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}"
        )

    except ObjectDoesNotExist as e:
        # Обработка отсутствия объектов
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Объектов нет: {str(e)}"
        )

# @router.post("/event/get-all-events")
# def get_all_events(filter_data: dict):
#     try:
#         search_text = filter_data.get("search_text")
#         date_start = filter_data.get("date_start")
#         date_end = filter_data.get("date_end")
#         event_category = filter_data.get("event_category")
        
#         # Создание динамического фильтра на основе переданных данных
#         filters = Q()

#         if search_text:
#             filters &= Q(name__icontains=search_text) | Q(description__icontains=search_text)
#         if date_start:
#             filters &= Q(datetime_of_event__gte=date_start)
#         if date_end:
#             filters &= Q(datetime_of_event__lte=date_end)
#         if event_category:
#             filters &= Q(event_category__name=event_category)
        
#         # Применение фильтров к запросу
#         events = Event.objects.filter(filters)
        
#         result = []

#         for event in events:
#             event_data = {
#                 "event_id": event.pk,
#                 "event_name": event.name,
#                 "event_description": event.description,
#                 "event_latitude": event.latitude,
#                 "event_longitude": event.longitude,
#                 "event_datetime": str(event.datetime_of_event),
#                 "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image}",
#                 "event_organizator_user_profile": {
#                     "event_organizator_user_profile_id": event.organizator.pk,
#                     "event_organizator_user_profile_role": {
#                         "event_organizator_user_profile_role_id": event.organizator.role.pk,
#                         "event_organizator_user_profile_role_name": event.organizator.role.name,
#                         "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
#                     },
#                     "event_organizator_user": {
#                         "event_organizator_user_id": event.organizator.user.pk,
#                         "event_organizator_user_username": event.organizator.user.username,
#                         "event_organizator_user_email": event.organizator.user.email,
#                         "event_organizator_user_first_name": event.organizator.user.first_name,
#                         "event_organizator_user_last_name": event.organizator.user.last_name
#                     },
#                 },
#             }
#             result.append(event_data)

#         return result

#     except ValueError as e:
#         # Обработка ошибок преобразования типов данных или других исключений
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}"
#         )

#     except ObjectDoesNotExist as e:
#         # Обработка отсутствия объектов
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Объектов нет: {str(e)}"
#         )
        
        
@router.post("/event/get-event")
def get_event(event_id: int):
    
    try:
        event = Event.objects.get(id=event_id)
        

        return {
            "event_id": event.pk,
            "event_name": event.name,
            "event_description": event.description,
            "event_category": event.event_category.name,
            "event_address": event.address,
            "event_start": event.datetime_start,
            "event_end": event.datetime_end,
            "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app/media/{event.image.url.split('media')[-1]}",
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

    
    except ValueError as e:
        # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

    except ObjectDoesNotExist as e:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Данный объект не существует: {str(e)}")
        
    except Exception as e:
        print(str(e))
        raise Exception( {
            
            "msg": f"{str(e)}"
        }
        )
        
        
@router.get("/event/get-all-cats")
def get_all_categories():
    cats = EventCategory.objects.all()

    result = []

    for cat in cats:
        cat_data = {
            "value": str(cat.name),
            "label": str(cat.name),
        }
        result.append(cat_data)

    return result


class EventData(BaseModel):
    name: str
    description: str
    eventDateStart: str
    eventDateEnd: str
    address: str
    image: str
    userId: int
    eventCategory: dict

@router.post("/event/post-event")
def post_event(request: EventData):
    try:
        # password: str, email: str, role: dict, first_name: str, last_name: str

        # if not event:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите данные")

        # print(event)

        name = request.name
        description = request.description
        event_datetime_start = str(request.eventDateStart)
        event_datetime_end = str(request.eventDateEnd)
        address = request.address
        image = request.image
        user_id = request.userId
        event_category = request.eventCategory["select"]["value"]
        

        print(event_category)
        

        # print(image)

        
        # name = event["name"]
        # organizator_id = event["userId"]
        # description = event["description"]
        # category_name = event["eventCategory"]["select"]["value"]
        # latitude = event["latitude"]
        # longitude = event["longitude"]
        # event_datetime = event["eventDateTime"]
        # image = image
        

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Название не указано")

        # if not latitude:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите широту")

        # if not longitude:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите долготу")
            

        with transaction.atomic():
            print(event_category)
            event_category = EventCategory.objects.get(name=event_category)
            
            
            organizator = UserProfile.objects.get(user__id=user_id)
            
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            image_binary = base64.b64decode(imgstr)

            media_path = os.path.join('media', 'events', f"{user_id}-{name}.{ext}")
            with open(media_path, 'wb') as fdst:
                fdst.write(image_binary)
                
                
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)
            print(media_path)

            
            event_created = Event.objects.create(
                name=name,
                description=description,
                event_category=event_category,
                address=address,
                datetime_start=event_datetime_start,
                datetime_end=event_datetime_end,
                image=media_path,
                organizator=organizator,
            )
            
            event_created.save()


            return {
                "ok": True,
                "detail": f"Мероприятие успешно добавлено!",
                "data": {
                    "event_id": event_created.pk,
                    "event_name": event_created.name,
                    "event_description": event_created.description,
                    "event_address": event_created.address,
                    "event_datetime_start": event_created.datetime_start,
                    "event_datetime_end": event_created.datetime_end,
                    "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app/media{event_created.image.url.split('media')[-1]}",
                    "event_category": {
                        "event_category_id": event_created.event_category.pk,
                        "event_category_name": event_created.event_category.name,
                        "event_category_color": event_created.event_category.color_hex,
                        },
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

    
    
    # try:
    #     event = Event.objects.c(id=event_id)
        
    #     result = []
    #     event_data = {
    #         "event_id": event.pk,
    #         "event_name": event.name,
    #         "event_description": event.description,
    #         "event_latitude": float(event.latitude),
    #         "event_longitude": float(event.longitude),
    #         "event_datetime": str(event.datetime_of_event),
    #         "event_image_url": f"https://dog-central-thoroughly.ngrok-free.app{event.image.url}",
    #         "event_organizator_user_profile": {
    #             "event_organizator_user_profile_id": event.organizator.pk,
    #             "event_organizator_user_profile_role": {
    #                 "event_organizator_user_profile_role_id": event.organizator.role.pk,
    #                 "event_organizator_user_profile_role_name": event.organizator.role.name,
    #                 "event_organizator_user_profile_role_is_can_post_event": event.organizator.role.is_can_post_event,
    #             },
    #             "event_organizator_user": {
    #                 "event_organizator_user_id": event.organizator.user.pk,
    #                 "event_organizator_user_username": event.organizator.user.username,
    #                 "event_organizator_user_email": event.organizator.user.email,
    #                 "event_organizator_user_first_name": event.organizator.user.first_name,
    #                 "event_organizator_user_last_name": event.organizator.user.last_name
    #             },
    #         },
    #     }
    #     result.append(event_data)

    #     return result
    
    # except ValueError as e:
    #     # Обработка ошибок преобразования типов данных, если не удаётся преобразовать в float, например, широту или долготу.
    #     raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}")

    # except ObjectDoesNotExist as e:
    #     raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail=f"Данный объект не существует: {str(e)}")


@router.get("/event/get-calendar-data")
# @router.post("/event/get-all-events")
def get_calendar_data(search_text: Optional[str] = None, date_start: Optional[str] = None, date_end: Optional[str] = None, event_category: Optional[str] = None):
    try:
        # if filter_data:
        #     search_text = filter_data.get("search_text")
        #     date_start = filter_data.get("date_start")
        #     date_end = filter_data.get("date_end")
        #     event_category = filter_data.get("event_category")
        
        # Создание динамического фильтра на основе переданных данных
        filters = Q()

        if search_text:
            filters &= Q(name__icontains=search_text) | Q(description__icontains=search_text)
        if date_start:
            filters &= Q(datetime_of_event__gte=date_start)
        if date_end:
            filters &= Q(datetime_of_event__lte=date_end)
        if event_category:
            filters &= Q(event_category__name=event_category)
        
        # Применение фильтров к запросу
        events = Event.objects.filter(filters)
        
        result = []

        for event in events:
            calendar_data = {
                "id": event.pk,
                "title": event.name,
                "start": event.datetime_start,
                "end": event.datetime_end,
                "color": event.event_category.color_hex,
                
            }
            result.append(calendar_data)

        return result

    except ValueError as e:
        # Обработка ошибок преобразования типов данных или других исключений
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ошибка: {str(e)}"
        )

    except ObjectDoesNotExist as e:
        # Обработка отсутствия объектов
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Объектов нет: {str(e)}"
        )