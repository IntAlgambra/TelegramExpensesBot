from flask import Flask
from flask import request

from flask_sslify import SSLify

import time

import telebot

from bot import bot

#url для webhook рабочего бота
BOT_WEBHOOK = ''

app = Flask(__name__)
sslify = SSLify(app)

#Обработчки запросов от телеги к рабочему боту
@app.route('/', methods = ['POST', 'GET'])
def bot_app():
    if request.method == 'POST':
        update_json = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(update_json)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return('go away')


#на всякий случай сбрасываем вебхук (если, например, сменили адрес)
bot.remove_webhook()

time.sleep(0.1)

#Устанавливаем вебхуки на ботов
bot.set_webhook(url = BOT_WEBHOOK)

if __name__ == '__main__':
    app.run()