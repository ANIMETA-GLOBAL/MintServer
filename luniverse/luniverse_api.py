import requests
import config
from pprint import pprint as pp


class Luniverse(object):

    def __init__(self):
        self.secrect_key = config.luniverse_secret_key
        self.access_key = config.luniverse_access_key
        self.token = None

        try:
            self.auth_token()
        except Exception as e:
            print(e)
        self.headers = {
            "Authorization": "Bearer " + self.token
        }

    def auth_token(self, expiresIn=315360000):

        url = "https://api.luniverse.io/svc/v2/auth-tokens"
        data = {
            "accessKey": self.access_key,
            "secretKey": self.secrect_key,
            "expiresIn": 315360000
        }
        res = requests.post(url, json=data)
        result = res.json()

        pp(result)

        if result['result'] == True:
            self.token = result['data']['authToken']['token']

        return res

    def get_nft_contract_detail(self, conrtactId):
        url = f"https://api.luniverse.io/svc/v2/nft/contracts/{conrtactId}"

        res = requests.get(url, headers=self.headers)

        return res.json()


if __name__ == '__main__':

    A = Luniverse()
    # print(A.auth_token().json())
    print(A.get_nft_contract_detail("1525706082614227204"))
