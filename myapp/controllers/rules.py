import os, json, traceback
from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotFound, HttpResponseBadRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
from manage import PATH
from typing import ItemsView, TypedDict
from datetime import datetime

class patch_params(TypedDict):
    rules: str

def getRules():
    path = os.path.join(PATH, 'assets', 'rules.md')
    
    
    try:
        file = open(path, 'r', encoding='UTF-8')

        content = file.read()
        file.close()

        modified_at = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%d. %m. 20%y')

        return HttpResponse(json.dumps({"rules": content, "modifiedAt": modified_at}), status=200)
    
    except FileNotFoundError:
        return HttpResponseNotFound()
    
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()
    

def postRules(files: ItemsView[str, InMemoryUploadedFile]):
    try:
        for name, file in files:
            if name.endswith('.md') or name.endswith('.txt'):
                dst_path = os.path.join(PATH, 'assets', 'rules.md')  
                
                dst = open(dst_path, 'wt', encoding='UTF-8')
                decoded_content = file.read().decode('UTF-8').strip()  
                lines = decoded_content.splitlines()
                content_to_write = '\n'.join(lines)
                dst.write(content_to_write)
                dst.close()
                
                return HttpResponse(status=204)
            
        return HttpResponseBadRequest(json.dumps({"error": "Treba poslať markdown súbor."}))
    
    except Exception:
        return HttpResponseServerError()
    

def patchRules(params: patch_params):
    try:
        path = os.path.join(PATH, 'assets', 'rules.md')
        dst = open(path, 'wt', encoding='UTF-8')

        dst.write(params['rules'])

        return HttpResponse(status=204)

    except Exception:
        return HttpResponseServerError()