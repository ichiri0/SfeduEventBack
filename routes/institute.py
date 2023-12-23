# from app.models import Group
import json
from django.core.asgi import get_asgi_application
import os
from fastapi import APIRouter
from fastapi import HTTPException
from asgiref.sync import sync_to_async


router = APIRouter()

# Укажите путь к вашим настройкам Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SfeduEventBack.settings")

django_app = get_asgi_application()

from app.models import Institute, Direction, Departament, Group


@router.get("/institute/all-institutes/")
def get_all_institutes():
    institutes = Institute.objects.all()
    result = []

    for institute in institutes:
        institutes_data = {
            "institute_id": institute.pk,
            "institute_name": institute.name,
            "institute_description": institute.description,
        }
        result.append(institutes_data)

    return result


@router.get("/institute/get-institute/")
def get_institute(institute_id: int):
    try:
        institute = Institute.objects.get(id=institute_id)
        institute_data = {
            "institute_id": institute.pk,
            "institute_name": institute.name,
            "institute_description": institute.description,
        }
        return institute_data
    except Institute.DoesNotExist:  # Обработка случая отсутствия института
        raise HTTPException(status_code=404, detail="Такого Института не существует")






@router.get("/institute/all-directions/")
def get_all_directions():
    directions = Direction.objects.all()
    result = []

    for direction in directions:
        directions_data = {
            "direction_id": direction.pk,
            "direction_name": direction.name,
            "direction_description": direction.description,
            "institute": {
                "institute_id": direction.institute.pk,
                "institute_name": direction.institute.name,
                "institute_description": direction.institute.description,
            },
        }
        result.append(directions_data)

    return result


@router.get("/institute/get-direction/")
def get_direction(direction_id: int):
    try:
        direction = Direction.objects.get(id=direction_id)
        direction_data = {
            "direction_id": direction.pk,
            "direction_name": direction.name,
            "direction_description": direction.description,
            "institute": {
                "institute_id": direction.institute.pk,
                "institute_name": direction.institute.name,
                "institute_description": direction.institute.description,
            },
        }
        return direction_data
    except Direction.DoesNotExist:  # Обработка случая отсутствия института
        raise HTTPException(status_code=404, detail="Такого Направления не существует")


@router.get("/institute/all-departaments/")
def get_all_institutes():
    departaments = Departament.objects.all()
    result = []

    for departament in departaments:
        departament_data = {
            "departament_id": departament.pk,
            "departament_name": departament.name,
            "departament_description": departament.description,
            "direction": {
                "direction_id": departament.direction.pk,
                "direction_name": departament.direction.name,
                "direction_description": departament.direction.description,
                "institute": {
                    "institute_id": departament.direction.institute.pk,
                    "institute_name": departament.direction.institute.name,
                    "institute_description": departament.direction.institute.description,
                },
            },
        }
        result.append(departament_data)

    return result


@router.get("/institute/get-departament/")
def get_departament(departament_id: int):
    try:
        departament = Departament.objects.get(id=departament_id)
        departament_data = {
            "departament_id": departament.pk,
            "departament_name": departament.name,
            "departament_description": departament.description,
            "direction": {
                "direction_id": departament.direction.pk,
                "direction_name": departament.direction.name,
                "direction_description": departament.direction.description,
                "institute": {
                    "institute_id": departament.direction.institute.pk,
                    "institute_name": departament.direction.institute.name,
                    "institute_description": departament.direction.institute.description,
                },
            },
        }
        return departament_data
    except Direction.DoesNotExist:  # Обработка случая отсутствия института
        raise HTTPException(status_code=404, detail="Такого Направления не существует")


@router.get("/institute/all-groups/")
def get_all_groups():
    groups = Group.objects.all()
    result = []

    for group in groups:
        group_data = {
            "group_id": group.pk,
            "group_full_name": group.full_name,
            "group_course": group.group_course.course_stage,
            "group_description": group.description,
            "departament": {
                "departament_id": group.departament.pk,
                "departament_name": group.departament.name,
                "departament_description": group.departament.description,
                "direction": {
                    "direction_id": group.departament.direction.pk,
                    "direction_name": group.departament.direction.name,
                    "direction_description": group.departament.direction.description,
                    "institute": {
                        "institute_id": group.departament.direction.institute.pk,
                        "institute_name": group.departament.direction.institute.name,
                        "institute_description": group.departament.direction.institute.description,
                    },
                },
            },
        }
        result.append(group_data)

    return result




@router.get("/institute/get-group/")
def get_group(group_id: int):
    try:
        group = Group.objects.get(id=group_id)
        group_data = {
            "group_id": group.pk,
            "group_full_name": group.full_name,
            "group_course": group.group_course.course_stage,
            "group_description": group.description,
            "departament": {
                "departament_id": group.departament.pk,
                "departament_name": group.departament.name,
                "departament_description": group.departament.description,
                "direction": {
                    "direction_id": group.departament.direction.pk,
                    "direction_name": group.departament.direction.name,
                    "direction_description": group.departament.direction.description,
                    "institute": {
                        "institute_id": group.departament.direction.institute.pk,
                        "institute_name": group.departament.direction.institute.name,
                        "institute_description": group.departament.direction.institute.description,
                    },
                },
            },
        }
        return group_data
    except Direction.DoesNotExist:  # Обработка случая отсутствия института
        raise HTTPException(status_code=404, detail="Такого Направления не существует")
