from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db import connection


def my_view(request, param):
    if request.method == "POST":
        body_param = request.POST.get("body_param")
        # Handle the request body parameter

    # Handle the URL parameter
    response_data = {"url_param": param, "message": "Hello, Django!"}
    return JsonResponse(response_data)


def hello(request):
    with connection.cursor() as c:
        c.execute(
            """
                SELECT VERSION()
            """
        )
        results = c.fetchall()
        for row in results:
            print(row[0])

    return HttpResponse("<h1>Hello Word</h1>")
