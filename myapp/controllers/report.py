from django.http import HttpResponse, HttpResponseBadRequest
from typing import ItemsView
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from manage import PATH

FILE_PATH = os.path.join(PATH, "media\\")


def fileUpload(files: ItemsView[str, InMemoryUploadedFile], form: ItemsView[str, str]):
    for key, value in form:
        print(key, value)
    for name, file in files:
        with open(FILE_PATH + name + ".png", "wb") as dst:
            for chunk in file.chunks():
                dst.write(chunk)
    return HttpResponse(status=200)
