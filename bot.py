import os

import telebot
import click
import dotenv

from backend import Backend

#Получаем токен бота из переменной среды (или вставляем свой)
dotenv.load_dotenv()
token = os.getenv('EXPENSES_BOT_TOKEN')

bot = telebot.TeleBot(token)
backend = Backend()

@bot.message_handler(commands = ['start'])
def send_welcoome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, backend.help_message)

@bot.message_handler(commands = ['help'])
def send_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, backend.help_message)

@bot.message_handler(commands = ['add'])
def add_account(message):
    msg = bot.reply_to(message, 'введите начальный баланс')
    bot.register_next_step_handler(msg, process_balance)

def process_balance(message):
    chat_id = message.chat.id
    balance = int(message.text)
    backend.create_account(chat_id, balance)
    bot.reply_to(message, 'аккаунт создан')

@bot.message_handler(commands = ['get_balance'])
def get_balance(message):
    chat_id = message.chat.id
    balance = backend.get_balance(chat_id)
    if balance:
        bot.reply_to(message, 'your balance: {}'.format(balance))
    else:
        bot.reply_to(message, 'Oops! Something went wrong((')

@bot.message_handler(commands = ['update_balance'])
def update_balance(message):
    msg = bot.reply_to(message, 'введите новый баланс')
    bot.register_next_step_handler(msg, process_update_balance)

def process_update_balance(message):
    chat_id = message.chat.id
    new_balance = int(message.text)
    if backend.update_balance(chat_id, new_balance):
        bot.reply_to(message, 'Your balance was updated')
    else:
        bot.reply_to(message, 'Ooops, something went wrong...')

@bot.message_handler(commands = ['get_today_outcomes'])
def get_today_outcomes(message):
    outcomes = backend.get_today_outcomes(message.chat.id)
    bot.reply_to(message, outcomes)

@bot.message_handler(commands = ['get_csv_outcomes'])
def get_csv_outcomes(message):
    chat_id = message.chat.id
    status = backend.get_csv_outcomes(chat_id)
    if status:
        csv_file = open('temp/{}-outcomes.csv'.format(chat_id), mode='rb')
        bot.send_document(chat_id, csv_file)
        csv_file.close()
        os.remove('temp/{}-outcomes.csv'.format(chat_id))
    else:
        bot.reply_to(message, 'somrthing went wrong')

@bot.message_handler()
def process_message(message):
    chat_id = message.chat.id
    text = message.text
    new_balance = backend.process_transaction(chat_id, text)
    if new_balance:
        bot.reply_to(message, 'Noted! New balance: {}'.format(new_balance))
    else:
        bot.reply_to(message, "Sorry, can't recognize your message")

@click.group()
def start():
    pass

@start.command(help='starts bot without proxy')
def start_bot():
    bot.polling()

@start.command(help='starts bot with passing traffic through tor on port 9150 (TOR need to be launched)')
def start_tor_bot():
    telebot.apihelper.proxy = {'https': 'socks5://127.0.0.1:9150'}
    bot.polling()

if __name__ == '__main__':
    start()