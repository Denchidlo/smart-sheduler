from typing import Any
import requests as req
from requests.exceptions import HTTPError
import json

class BsuirRequester:
    def __init__(self) -> None:
        self.stopped = False

    def send_request(self, request_string: str) -> Any:
        responce = req.get(request_string)
        if responce.status_code != 200:
            raise HTTPError(f"Request aborted!\nRequest string: '{request_string}'\nStatus code: {responce.status_code}\nDetailed info: {responce.reason}")
        else:
            responce = responce.json()
        return responce

    def create_session(self):
        self.stopped == False
        while not self.stopped:
            try:
                print("> ", end='')
                str = input()
                try:
                    responce = self.send_request(str)
                    with open("last_responce.json", "wt") as writer:
                        json.dump(responce, writer)
                except HTTPError as err:
                    responce = err.msg
                print(f"Request: {str}\nResponce info:\n============\n{responce}")
            except EOFError:
                print('\n|--> Stopped <--|')
                self.stopped = True
                continue
            except KeyboardInterrupt:
                print('\n|--> Stopped <--|')
                self.stopped = True
                continue