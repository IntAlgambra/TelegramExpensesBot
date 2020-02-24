# Project Title

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Dependencies](#dependencies)
- [Installing](#installing)
- [Usage](#usage)

## About <a name = "about"></a>

SimpleExpenseBot - telegram bot for managing your finance. What in can do:

1. Manage your incomes and outcomes and track your balance

2. Return your incomes and outcomes in text format in telegram

3. Return your incomes and outcomes in .csv file to import it in excel

## Getting Started <a name = "getting_started"></a>

1. Create python virtual environment with virtualenv or something similar

2. Create environment variable "EXPENSE_BOT_TOKEN" with your bot token

## Dependencies <a name = "dependencies"></a>

This bot using several python libraries:

1. pyTelegramBotAPI for working with telegram API

2. sqlalchemy for managing sqlite database

3. click for command line interface

## Installing <a name = "installing"></a>

To install simple run command

```
git clone 
```

Activate virtual environment and install all required libraries

```
pip install -r requirements.txt
```

## Usage <a name = "usage"></a>

If you are in Russia, download, install and launch Tor Browser. Then run

```
python bot.py start-tor-bot
```

If Telegram is working in your country just run

```
python bot.py start-bot
```

or you can just use my bot to manage your finance: https://t.me/@SimpleExpenseBot 
