import requests
import json
from execptions import InvalidLogin, InvalidURL, InvalidMethod, InvalidServerState


class API:
    def __init__(self, url: str, username: str, password: str):
        if url[-1] == "/":
            url = url[:-1]
        self.url = url
        self.username = username
        self.password = password
        self.token = None
        self._auth()

    def _auth(self):
        try:
            resp = requests.post(self.url+"/auth", json={"username": self.username, "password": self.password})
        except (json.JSONDecodeError, KeyError):
            raise InvalidLogin
        except requests.exceptions.ConnectionError:
            raise ConnectionError
        except requests.exceptions.MissingSchema:
            raise InvalidURL
        else:
            self.token = {"Authorization": f"jwt {resp.json()['access_token']}"}

    def _request(self, args: str, body=None, method: str = "get"):
        if body is None:
            body = dict()

        if method == "get":
            resp = requests.get(self.url+args, headers=self.token, json=body)
        elif method == "put":
            resp = requests.put(self.url + args, headers=self.token, json=body)
        elif method == "post":
            resp = requests.post(self.url+args, headers=self.token, json=body)
        else:
            raise InvalidMethod

        if resp.status_code == 401:
            self._auth()
            return self._request(args, body, method)
        else:
            return resp

    def code_400(self, text: str):
        if "not running" in text:
            msg = "Server is not running"
        elif "running" in text:
            msg = "Server is running"
        elif "respond" in text:
            msg = "Server did not respond"
        else:
            msg = text
        raise InvalidServerState(msg)

    def status(self):
        resp = self._request("/")
        if resp.status_code == 400 or "offline" in resp.text:
            return False
        else:
            ps = resp.text.find("has")
            pe = resp.text.find("players", ps)
            p = int(resp.text[ps+3:pe])
            ls = resp.text.find("in", pe)
            le = resp.text.find("ms", ls)
            lt = float(resp.text[ls+2:le])
            pls = resp.text.find("players: ", le)
            pl = resp.text[pls+9:].split(", ")
            return p, lt, pl

    def start(self):
        resp = self._request("/start")
        if resp.status_code == 400:
            self.code_400(resp.text)
        else:
            return True

    def stop(self):
        resp = self._request("/stop")
        if resp.status_code == 400:
            self.code_400(resp.text)
        else:
            return resp.text

    def kill(self):
        resp = self._request("/kill")
        if resp.status_code == 400:
            self.code_400(resp.text)
        else:
            return True

    def cmd(self, cmd):
        resp = self._request("/cmd", {"command": cmd}, "post")
        if resp.status_code == 400:
            self.code_400(resp.text)
        else:
            return resp.text

    def logs(self):
        resp = self._request("/logs")
        if resp.status_code == 400:
            self.code_400(resp.text)
        else:
            return resp.text
