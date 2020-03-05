import os

from flask import Flask
from flask import request
from flask import abort
from flask_sslify import SSLify
import dotenv
import telebot

from bot import bot, set_proxy

dotenv.load_dotenv

HOSTNAME = os.getenv('WEBHOOK_BASE')
TOKEN = os.getenv('EXPENSES_BOT_TOKEN')

webhook_url = '{}/{}/'.format(HOSTNAME, TOKEN)
webhook_path = '/{}/'.format(TOKEN)

print(webhook_url, webhook_path)

# uncomment this line to redirect bot requests through TOR
# set_proxy()

app = Flask(__name__)
sslify = SSLify(app)

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'Bot server test success!'

@app.route(webhook_path, methods=['POST'])
def process_updates():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

if __name__ == '__main__':
    app.run()