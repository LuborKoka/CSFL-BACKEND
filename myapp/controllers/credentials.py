from typing import List, TypedDict
from ..models import UsersRoles
from django.http import HttpResponseForbidden, HttpRequest
import jwt
from ..views_folder.userViews import SECRET_KEY


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
    except Exception:
        return HttpResponseForbidden()

    try:
        roles = UsersRoles.objects.filter(user_id=data["id"]).select_related("role")

        if len(roles) == 0:
            return HttpResponseForbidden()

        for r in roles:
            if r.role.name in requiredRoles:
                return True

        return HttpResponseForbidden()

    except jwt.ExpiredSignatureError:
        # Handle expired token
        return HttpResponseForbidden(
            "Platnosť prihlásenia vypršala. Prosím, znova sa prihlás."
        )

    except Exception as e:
        print(e)
        # Handle other unexpected exceptions
        return HttpResponseForbidden()


def tokenFromHeader(header: str):
    if header.startswith("Bearer "):
        return header[len("Bearer ") :].strip()

    return header
