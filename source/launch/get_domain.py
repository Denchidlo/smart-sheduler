import pathlib
import json
from os import environ

PATH = str(pathlib.Path(__file__).parent.parent.absolute())
APP_PATH = str('/'.join(PATH.split('/')[:-1]))
try:
    with open(f'{PATH}/ngrok_tmp.json', 'r') as domain_reader:
        ngrok_responce = json.load(domain_reader)
        with open(f'{APP_PATH}/baseapp/appsettings.json', 'r') as config_reader:
            appconfig = json.load(config_reader)
        tunnel = ngrok_responce["tunnels"][0]
        print('\n\tServer public domain: "{domain}"\n'.format(domain=tunnel['public_url'][8:]))
        if tunnel['proto'] == 'http':
            appconfig['domain'] = tunnel['public_url'][7:]
        elif tunnel['proto'] == 'https':
            appconfig['domain'] = tunnel['public_url'][8:]
        else:
            raise ValueError("Wrong domain occured")
        with open(f'{APP_PATH}/baseapp/appsettings.json', 'w') as config_writer:
            json.dump(appconfig, config_writer)
except Exception as ex:
    print(f'Exception occured:\n\tInformation:\n{ex.__str__()}\n\tTraceback:\n{ex.with_traceback().__str__()}')