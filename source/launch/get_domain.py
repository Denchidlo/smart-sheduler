import pathlib
import json
from os import environ

PATH = pathlib.Path(__file__).parent.parent.absolute()

try:
    with open(f'{PATH}/launch/ngrok_tmp.json', 'r') as domain_reader:
        ngrok_responce = json.load(domain_reader)
        with open(f'{PATH}/{environ["APP_NAME"]}/appconfig.json', 'r') as config_reader:
            appconfig = json.load(config_reader)
        tunnel = ngrok_responce["tunnels"][0]
        if tunnel['proto'] == 'http':
            appconfig['domain'] = tunnel['public_url'][7:]
        with open(f'{PATH}/{environ["APP_NAME"]}/appconfig.json', 'r') as config_writer:
            json.dump(config_writer)
except Exception as ex:
    print(ex.__str__())