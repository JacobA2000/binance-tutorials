import requests
import config

def send_message(msg):
    data = {'content': msg}
    result = requests.post(config.DISCORD_WEBHOOK_URL, json=data)

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print(f'Discord message delivered successfully, code {result.status_code}.')