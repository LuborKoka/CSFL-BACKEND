from typing import List, TypedDict
from ..models import UsersRoles, Users, Roles
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
import jwt
from ..views_folder.userViews import SECRET_KEY


class DataType(TypedDict):
    username: str
    id: str


# returns true/403 forbidden
def isUserPermitted(header: str | None, requiredRoles: List[str]):
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
