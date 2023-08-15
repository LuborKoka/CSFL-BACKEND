from ..models import Users, DiscordAccounts
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.db import connection
from typing import TypedDict
import traceback, json, os, requests

class UserDiscordParams(TypedDict):
    userID: str
    code: str

    
DISCORD_API_URI = 'https://discord.com/api/v10'
CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
REDIRECT_URI = 'http://192.168.100.22:3000/verify-user'



def save_user_discord(params: UserDiscordParams):
    if 'userID' not in params:
        return HttpResponseBadRequest(json.dumps({"error": 'Treba sa prihlásiť.'}))
    

    try:
        access_token_response = exchange_code(params['code'])
        user_data = get_user_data(access_token_response['access_token'])
    except Exception:
        return HttpResponseServerError(json.dumps({"error": "Nepodarilo sa získať dáta z discordu."}))

    c = connection.cursor()

    database_data = [user_data['id'], user_data['username'], user_data['global_name'], user_data['avatar'], access_token_response['expires_in'], access_token_response['refresh_token'], params['userID']]

    try:
        c.execute("""
            INSERT INTO discord_accounts (discord_id, discord_username, discord_global_name, discord_avatar, expires_at, refresh_token, user_id)
            VALUES
                (%s, %s, %s, %s, NOW() + make_interval(secs := %s), %s, %s)
            RETURNING id
        """, database_data)

        discord_account_id = c.fetchone()[0]

        dc_acc = DiscordAccounts.objects.get(id=discord_account_id)

        user = Users.objects.get(id = params['userID'])
        user.discord_account= dc_acc
        user.save()

        return HttpResponse(status=204)
        
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError(json.dumps({
            "error": "Nepodarilo sa prepojiť tvoj discord účet."
        }))



def exchange_code(code: str):
    data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
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
    response = requests.get('%s/users/@me' % DISCORD_API_URI, headers=headers)
    response.raise_for_status()
    return response.json()
