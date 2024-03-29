from ..models import Users, DiscordAccounts
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse
from django.db import connection, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from typing import TypedDict
import traceback, json, os, requests

class UserDiscordParams(TypedDict):
    userID: str
    code: str

    
DISCORD_API_URI = 'https://discord.com/api/v10'
CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
REDIRECT_BASE_URL = 'http://192.168.100.22:3000' #'http://csfl.cz'
GUILD_ID = os.environ.get('CSFL_GUILD_ID')



def save_user_discord(params: UserDiscordParams):
    if 'userID' not in params:
        return HttpResponseBadRequest(json.dumps({"error": 'Treba sa prihlásiť.'}))
    

    try:
        access_token_response = exchange_code(params['code'])
        user_data = get_user_data(access_token_response['access_token'])

    except Exception:
        return HttpResponseServerError(json.dumps({"error": "Nepodarilo sa získať dáta z discordu."}))

    c = connection.cursor()

    premium_type = user_data['premium_type'] if user_data['premium_type'] is not None else 0

    database_data = [user_data['id'], user_data['username'], user_data['global_name'], user_data['avatar'], access_token_response['expires_in'], 
        access_token_response['refresh_token'], params['userID'], premium_type, user_data['accent_color'], user_data['banner'], 
        user_data['banner_color'], user_data['avatar_decoration']]

    try:
        c.execute("""
            INSERT INTO discord_accounts (discord_id, discord_username, discord_global_name, discord_avatar, expires_at, refresh_token, user_id, premium_type, accent_color, banner, banner_color, avatar_decoration)
            VALUES
                (%s, %s, %s, %s, NOW() + make_interval(secs := %s), %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, database_data)

        discord_account_id = c.fetchone()[0]

        dc_acc = DiscordAccounts.objects.get(id=discord_account_id)

        user = Users.objects.get(id = params['userID'])
        user.discord_account= dc_acc
        user.save()

        c.close()
        return JsonResponse({"is_member": user_data["is_member"]})
        
    except IntegrityError:
        c.close()
        return HttpResponseBadRequest(json.dumps({
            "error": "Tento Discord účet už niekto používa."
        }))

    except Exception:
        c.close()
        traceback.print_exc()
        return HttpResponseServerError(json.dumps({
            "error": "Nepodarilo sa prepojiť tvoj discord účet."
        }))


def get_user_discord(userID: str):
    if userID == 'undefined':
        return HttpResponseNotFound()

    try:
        user = Users.objects.select_related('discord_account').get(id = userID)

    except ObjectDoesNotExist:
        return HttpResponseNotFound(json.dumps({
            "error": "Tento účet sa nenašiel. Skús sa znovu prihlásiť."
        }))

    except Exception:
        traceback.print_exc()
        return HttpResponseServerError(json.dumps({
            "error": "Niečo sa pokazilo, skús to znova."
        }))

    
    if user.discord_account is None:
        return HttpResponse(status=204)


    result = {
        "discord_id": str(user.discord_account.discord_id),
        "discord_username": user.discord_account.discord_username,
        "discord_global_name": user.discord_account.discord_global_name,
        "avatar": user.discord_account.discord_avatar,
        "premium_type": user.discord_account.premium_type
    }

    return HttpResponse(json.dumps(result), status=200)


def delete_user_discord(userID: str):
    try:
        user = Users.objects.select_related('discord_account').get(id = userID)

    except ObjectDoesNotExist:
        return HttpResponseNotFound(json.dumps({
            "error": "Takýto účet sme nenašli, skús sa znova prihlásiť."
        }))
    
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError(json.dumps({
            "error": "Niečo sa pokazilo, skús to znova."
        }))
    
    dc_acc = user.discord_account
    user.discord_account = None
    user.save()
    dc_acc.delete()

    return HttpResponse(status=204)



def exchange_code(code: str):
    data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_BASE_URL + '/verify-user'
    }
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % DISCORD_API_URI, data=data, headers=headers)
    r.raise_for_status()
    return r.json()


def get_user_data(access_token: str):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    guilds = requests.get('%s/users/@me/guilds' % DISCORD_API_URI, headers=headers)
    response = requests.get('%s/users/@me' % DISCORD_API_URI, headers=headers)
    response.raise_for_status()
    guilds.raise_for_status()
    data = response.json()

    result = {"id": data["id"], "username": data["username"]}
    result["global_name"] = data["global_name"] if "global_name" in data else None
    result["avatar"] = data["avatar"] if "avatar" in data else None
    result["avatar_decoration"] = data["avatar_decoration_data"] if "avatar_decoration_data" in data else None
    result["banner"] = data["banner"] if "banner" in data else None
    result["banner_color"] = data["banner_color"] if "banner_color" in data else None
    result["accent_color"] = data["accent_color"] if "accent_color" in data else None
    result["premium_type"] = data['premium_type'] if "premium_type" in data else 0

    for guild in guilds.json():
        if guild['id'] == GUILD_ID:
            result["is_member"] = True
            return result


    result["is_member"] = False
    
    return result
