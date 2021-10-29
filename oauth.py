import requests as rq


class OauthManager:
    @staticmethod
    def get_token_from_code(code):
        payload = {
            'client_id': '875813558611480587', # айди бота
            'client_secret': 'HEHAsbueetMVriU9FLUuZjIJU0uzohmm2', # клиент секрет бота
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'https://tornadodomain.000webhostapp.com/oauth'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = rq.post('https://discord.com/api/oauth2/token', headers=headers, data=payload)
        if r.status_code != 200:
            return False, 'Неверный code!'
        return True, r.json()['access_token'] 

