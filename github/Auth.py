from typing import Union, Optional
from pydantic import BaseModel
from time import time
from jwt import JWT, jwk_from_pem
import requests


class JwtToken(BaseModel):
    iss: int
    exp: Optional[int] = 300
    certificate_path: Optional[str] = "meme-bot-test.pem"
    iat: Optional[float] = None
    _token: str = None

    @property
    def token(self):
        if not self.__valid_token__:
            self._token = self.__encode_jwt__()
        return self._token

    @property
    def __certificate__(self):
        try:
            with open(self.certificate_path, "rb") as pem_file:
                certificate = jwk_from_pem(pem_file.read())
            return certificate
        except Exception as e:
            raise Exception(
                "An error occured when reading the certificate: \n {}".format(e)
            )

    @property
    def __valid_token__(self) -> bool:
        if self.iat:
            if int(time()) > (self.iat + self.exp):
                return False
            elif self._token:
                return True
        return False

    def __encode_jwt__(self):
        self.iat = time()
        payload = {
            "iat": int(self.iat),
            "exp": int(self.iat) + self.exp,
            "iss": self.iss,
        }
        token = JWT()
        return token.encode(
            payload,
            self.__certificate__,
            alg="RS256",
        )


class GitAppAuth:
    _installation_url: str = "https://api.github.com/app/installations"
    __certificate_path: str = "meme-bot-test.pem"
    __jwt_token: JwtToken = None

    def __init__(
        self,
        app_id: Union[int, str],
    ):
        self.app_id = app_id
        self.__jwt_token = JwtToken(iss=app_id)
        #self.__installation_id = self._get_installation_id()
        #self.__installation_token = self._get_installation_token()

    def _get_installation_id(self):
        if self.__installation_id:
            return self.__installation_id
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__jwt_token.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.get(self._installation_url, headers=headers)

        if response.status_code == 200:
            self.__installation_id = response.json()[0]["id"]
            return response.json()[0]["id"]

        raise Exception(f"Failed to get installation ID: {response.status_code}")

    def _get_installation_token(self):
        if self.__installation_token:
            return self.__installation_token
        url = f"{self._installation_url}/{self.__installation_id}/access_tokens"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__jwt_token.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.get(url, headers=headers)

        if response == 200:
            return response.json()[0]

    def place_labels(self, repo_name: str, pr_number: str, labels: list):
        url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/labels"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.__jwt_token.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        response = requests.put(url, headers=headers, data=labels)

        if response.status_code == 200:
            return "ok"

        raise Exception(f"Failed to place labels on PR")


