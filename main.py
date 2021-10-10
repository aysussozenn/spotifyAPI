import requests
import spotipy
import base64
import datetime
from urllib.parse import urlencode
import json

client_id = 'a0b3781c37af438f812c07ef3e338905'
client_secret = '3eaa6aa6f38e4c4e87bc5cb09c7678db'


class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret

        if client_secret is None or client_id is None:
            raise Exception("You must set client_id and client_secret")

        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client...")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token is None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def get_playlist(self, _id):
        return self.get_resource(_id, resource_type='playlists')

    def get_track(self, _id):
        return self.get_resource(_id, resource_type='tracks')

    def get_audio_features(self, _id):
        return self.get_resource(_id, resource_type='audio-features')

    def base_search(self, query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)

        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def search(self, query=None, search_type='artist'):
        if query is None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        query_params = urlencode({"q": query, "type": search_type.lower()})
        return self.base_search(query_params)


client = SpotifyAPI(client_id, client_secret)
#print(json.dumps(client.search({"track": "Dangerous Animals", "artist": "Arctic Monkeys", "album": "Humbug"}, search_type="track"), indent=1))
#data = client.get_audio_features('141YScqYkYhHPpqWhIBebc')
data = client.get_playlist("5hg53KxzqRRqFG2MuzoN3P?si=dd7be795b8ab42d4")
tracks=[]
audio_feat=[]
for i in data["tracks"]["items"]:
    tracks.append(i["track"]["id"])

for i in range(0,len(tracks)):
    audio_feat.append(client.get_audio_features(tracks[i]))


print(json.dumps(audio_feat,indent=2))





