from ..models import Users, UsersRoles, Roles
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
import json, traceback
from typing import TypedDict

class RoleParams(TypedDict):
    user_id: str
    role: str


def get_users():
    try:
        users = Users.objects.select_related('driver').all()
        user_roles = UsersRoles.objects.select_related('role', 'user').all()
        roles = Roles.objects.all()

    except Exception:
        traceback.print_exc()
        HttpResponseServerError()

    result = {"users": [], "roles": []}

    for u in users:
        user = {
            "user_id": str(u.id),
            "driver_id": str(u.driver.id),
            "driver_name": u.driver.name,
            "username": u.username,
            "roles": []
        }

        for ur in user_roles:
            if u.id == ur.user.id:
                user['roles'].append({
                    "role_id": str(ur.role.id),
                    "role_name": ur.role.name
                })
        result["users"].append(user)

    for r in roles:
        result['roles'].append({
            "role_id": str(r.id),
            "role_name": r.name
        })

    return HttpResponse(json.dumps(result), status=200)


def add_user_role(userID: str, roleID: str):
    try:
        with connection.cursor() as c:
            c.execute("""
                INSERT INTO users_roles (user_id, role_id)
                VALUES (%s, %s)
            """, [userID, roleID])

    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()

    return HttpResponse(status=204)




def delete_user_role(user_id: str, role_id: str):   
    try:
        role = UsersRoles.objects.get(user_id = user_id, role_id = role_id)

        role.delete()

        return HttpResponse(status=204)

    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({
            "error": "Táto rola neexistuje."
        }))
    
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()