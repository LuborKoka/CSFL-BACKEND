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

    except Exception:
        HttpResponseServerError()

    result = {"users": []}

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

    return HttpResponse(json.dumps(result), status=200)


def add_user_role(params: RoleParams):
    try:
        role = Roles.objects.get(name = params["role"])


    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({
            "error": "Táto rola neexistuje."
        }))
    
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()
    

    try:
        c = connection.cursor()
        c.execute("""
            INSERT INTO users_roles(user_id, role_id) 
            VALUES
                (%s, %s)
        """, [params["user_id"], str(role.id)])

        return HttpResponse(status=204)

    except Exception:
        return HttpResponseServerError()



def delete_user_role(user_id: str, role: str):   
    try:
        role = UsersRoles.objects.get(user_id = user_id, role__name = role)

        role.delete()

        return HttpResponse(status=204)

    except ObjectDoesNotExist:
        return HttpResponseBadRequest(json.dumps({
            "error": "Táto rola neexistuje."
        }))
    
    except Exception:
        return HttpResponseServerError()