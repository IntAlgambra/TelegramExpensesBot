from database import Database
import csv
import os

class Backend():

    @staticmethod
    def format_transactions(transactions):
        date = transactions[0]['date']
        head = '<{}>\n'.format(date)
        body = '\n----------\n'.join(['{} - {}'.format(t['amount'], t['description']) for t in transactions])
        footer = '\n__________'
        result = head + body + footer
        return result

    def __init__(self):
        self.db = Database()
        with open('help.txt', 'r') as f:
            self.help_message = f.read()
        #Проверяем наличие папки для сохранения временных csv файлов
        self.temp_path = 'temp/'
        if not os.path.exists(self.temp_path):
            os.mkdir('temp')


    def create_account(self, chat_id, balance):
        self.db.add_user(chat_id, balance)
    
    def process_transaction(self, chat_id, text):
        #Избавляемся от пробелов с концов строки
        text = text.strip()
        text_amount, description = (text.split()[0], ' '.join(text.split()[1:]))
        try:
            amount = abs(int(text_amount))
        except ValueError:
            return None
        if text_amount.startswith('+'):
            self.db.add_income(chat_id, amount, description)
        else:
            self.db.add_outcome(chat_id, amount, description)
        return self.db.get_balance(chat_id)

    def _process_transaction_with_day(self, chat_id, text, day):
        text = text.strip()
        text_amount, description = (text.split()[0], ' '.join(text.split()[1:]))
        try:
            amount = abs(int(text_amount))
        except ValueError:
            return None
        if text_amount.startswith('+'):
            return
            # self.db._add_income_free_date(chat_id, amount, description, day)
        else:
            self.db._add_outcome_free_date(chat_id, amount, description, day)
        return self.db.get_balance(chat_id)

    def update_balance(self, chat_id, balance):
        return self.db.update_balance(chat_id, balance)

    def get_balance(self, chat_id):
        return self.db.get_balance(chat_id)

    def del_last_transaction(self, chat_id):
        return self.db.del_last_transaction(chat_id)

    def get_today_outcomes(self, chat_id):
        today_outcomes = self.db.get_today_outcomes(chat_id)
        if not today_outcomes:
            return 'There was no outcomes today'
        response = self.format_transactions(today_outcomes)
        return response

    def get_outcomes_for_n_days(self, chat_id, days):
        outcomes = self.db.get_outcomes_for_n_days(chat_id, days)
        print(outcomes)
        result_array = []
        for day in reversed(sorted(outcomes)):
            result_array.append(self.format_transactions(outcomes[day]))
        return '\n'.join(result_array)

    def get_csv_outcomes(self, chat_id):
        outcomes = self.db.get_outcomes(chat_id)
        csv_file = open('temp/{}-outcomes.csv'.format(chat_id), mode='w')
        fieldnames = ['date', 'amount', 'description']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for outcome in outcomes:
            writer.writerow(outcome)
        csv_file.close()
        return 'ok'

