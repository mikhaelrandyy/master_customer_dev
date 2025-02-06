import requests
from schemas.oauth_sch import AccessToken
from typing import Tuple

from configs.config import settings

class OauthService:
    OAUTH_BASE_URL = settings.OAUTH2_URL
    OAUTH_DEFAULT_TOKEN = settings.OAUTH2_TOKEN

    NOT_AUTHORIZED = "Not authenticated"
    CONNECTION_FAILED = "Cannot create connection to authentication server."

    async def check_token(self, token) -> Tuple[AccessToken | None, str]:
        try:
            url = f'{self.OAUTH_BASE_URL}oauth/check_token/'
            headers = {'Authorization': f'Bearer {self.OAUTH_DEFAULT_TOKEN}'}
            body = {'token': token}
            response = requests.post(url=url, headers=headers, data=body)
            if response.status_code == 200:
                r = response.json()
                if r['active'] == False:
                    return None, self.NOT_AUTHORIZED
                else:
                    login_user = AccessToken(**r)
                    login_user.token = token
                    return login_user, "OK"
            else:
                return None, self.NOT_AUTHORIZED
        except:
            return None, self.CONNECTION_FAILED

    async def get_oauth_user(self, email, phone=None):
        url = "{}api/users/byemailormobile/{}".format(self.OAUTH_BASE_URL, email)
        url = url if phone is None else url + '/' + phone

        headers = {
            'Authorization': 'Bearer ' + str(self.OAUTH_DEFAULT_TOKEN)
        }
        response = requests.get(url, headers=headers)
        return response.json()['data']
        
    async def create_user_oauth(self, body):
        url_create_user = "{}api/users/".format(self.OAUTH_BASE_URL)

        headers = {
            'Authorization': 'Bearer ' + str(self.OAUTH_DEFAULT_TOKEN),
            'Content-Type': 'Application/Json'
        }
        response = requests.post(url_create_user, json=body, headers=headers)
        if 200 <= response.status_code <= 299:
            return response.json()['data']
        raise response

    async def update_user_oauth(self, body, id):
        url_update_user = '{}api/users/{}/'.format(self.OAUTH_BASE_URL, id)

        headers = {
            'Authorization': 'Bearer ' + str(self.OAUTH_DEFAULT_TOKEN),
            'Content-Type': 'Application/Json'
        }

        response = requests.put(url_update_user, json=body, headers=headers)
        if 200 <= response.status_code <= 299:
            return response.json()['data']
        return None