# SETUP THE BOT:
# search 'botfather' in telegram
# send '/newbot' to BotFather
# enter a NAME for the bot
# enter a USERNAME for the bot
# receive the bot's TOKEN
# assign the TOKEN to a variable
# get the CHAT ID via 'https://api.telegram.org/bot<TOKEN>/getUpdates' in the webbrowser

# LINK TO CURRENT TEST BOT
# t.me/aasche_test_bot

import requests
import yaml
import os
import json
from .models import Parameter

# load configfile
# configfile = yaml.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')), Loader=yaml.BaseLoader)

def telegram_bot_sendtext(bot_message):

    token = Parameter.objects.get(key="TELEGRAM_BOT_TOKEN")
    chat_id = Parameter.objects.get(key="TELEGRAM_BOT_CHAT_ID")

    send_text = f'https://api.telegram.org/bot{token.value}/sendMessage?chat_id={chat_id.value}&parse_mode=Markdown&text={bot_message}'

    response = requests.get(send_text)

    return response.json()

# test = telegram_bot_sendtext('Testing Telegram bot')





