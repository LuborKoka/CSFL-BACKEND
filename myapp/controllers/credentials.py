from typing import List, TypedDict
from ..models import UsersRoles
from django.http import HttpResponseForbidden
import jwt, traceback, json
from ..controllers.secrets import SECRET_KEY


class DataType(TypedDict):
    username: str
    id: str



def isUserPermitted(header: str | None, requiredRoles: List[str]) -> bool | HttpResponseForbidden:
    """
    A function to check user permissions for certain actions.
    
    Returns:
        True if user is permitted

        HttpResponseForbidden if not
    """

    if header == "":
        return HttpResponseForbidden()

    token = tokenFromHeader(header)

    try:
        data: DataType = jwt.decode(jwt=token, algorithms=["HS256"], key=SECRET_KEY)

    except jwt.ExpiredSignatureError:
        # Handle expired token
        return HttpResponseForbidden(json.dumps({
            "error": "Platnosť prihlásenia vypršala. Prihlás sa znova."
        }))
    
    except jwt.InvalidSignatureError:
        return HttpResponseForbidden(
            json.dumps({
            "error": "Platnosť prihlásenia skončila. Prihlás sa znova."
        }))
    
    except Exception:
        traceback.print_exc()
        return HttpResponseForbidden()
    
    if len(requiredRoles) == 0:
        return True

    try:
        roles = UsersRoles.objects.filter(user_id=data["id"]).select_related("role")

        if len(roles) == 0:
            return HttpResponseForbidden()

        for r in roles:
            if r.role.name in requiredRoles:
                return True

        return HttpResponseForbidden()

    except Exception:
        traceback.print_exc()
        # Handle other unexpected exceptions
        return HttpResponseForbidden()


def tokenFromHeader(header: str):
    if header.startswith("Bearer "):
        return header[len("Bearer ") :].strip()

    return header
