import requests
from dotenv import load_dotenv
import os 
from urllib.parse import urlencode

#Generate the Authorization URL
def get_auth_url(client_id, redirect_uri):
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "activity:read_all"
    }
    return f"https://www.strava.com/oauth/authorize?{urlencode(params)}"

def get_access_token(client_id, client_secret, code):
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch token: {response.status_code} {response.text}")
    
def get_activities(access_token,num_per_page =200):
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = {"per_page":num_per_page}
    headers = {"Authorization": f"Bearer {access_token}"}
    #print(headers)
    response = requests.get(url, params=params, headers=headers)
    #print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch activities: {response.status_code} {response.text}")
    
def get_secrets():
    load_dotenv()
    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    REDIRECT_URI = "http://localhost:8080/"
    return STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET,REDIRECT_URI