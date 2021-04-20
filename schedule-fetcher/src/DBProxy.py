from mysql.connector import Error,  connect
import json
from .bsuir_requests import BsuirRequester as Provider

class DBProxy:
    def __init__(self, connection_string) -> None:
        self.data_provider = Provider()
        self.connection_string = connection_string
        self.dbconnection = connect()

    def connect(self):
        pass
