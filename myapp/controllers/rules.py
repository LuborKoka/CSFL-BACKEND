import os, json, traceback
from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound
from manage import PATH

def getRules():
    path = PATH + os.sep + 'assets' + os.sep + 'rules.md'
    
    
    try:
        file = open(path, 'r', encoding='UTF-8')

        content = file.read()

        return HttpResponse(json.dumps({"rules": content}), status=200)
    
    except FileNotFoundError:
        return HttpResponseNotFound()
    
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()