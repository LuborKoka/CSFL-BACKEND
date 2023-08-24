from typing import TypedDict
from django.db import connection
from django.http import HttpResponseServerError, HttpResponse
import traceback

class CreateDriver(TypedDict):
    name: str

def createDriver(params: CreateDriver):
    try:
        with connection.cursor() as c:
            c.execute("""
                INSERT INTO drivers (name)
                VALUES (%s)
            """, [params['name']])

        return HttpResponse(status=204)


    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()
    


