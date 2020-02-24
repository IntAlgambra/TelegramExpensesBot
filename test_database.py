import unittest
import random
from datetime import date, timedelta

import database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = database.Database()
        cls.test_users = [
            {
                'chat_id': 123456,
                'balance': 100000,
            },
            {
                'chat_id': 234567,
                'balance': 200000,
            },
            {
                'chat_id': 345678,
                'balance': 300000,
            },
        ]

    def setUp(self):
        self.db.update_all()
        for user in self.test_users:
            self.db.add_user(user['chat_id'], user['balance'])

    def tearDown(self):
        pass

    def test_check_balance(self):
        chat_id = random.randint(100000, 999999)
        balance = random.randint(100000, 999999)
        self.db.add_user(chat_id, balance)
        user_balance = self.db.get_balance(chat_id)
        self.assertEqual(user_balance, balance )

    def test_update_balance(self):
        test_id = self.test_users[0]['chat_id']
        new_balance = random.randint(100000, 999999)
        check_1 = self.db.update_balance(test_id, new_balance)
        check_2 = self.db.get_balance(test_id)
        self.assertEqual(check_1, new_balance)
        self.assertEqual(check_2, new_balance)

    def test_add_income(self):
        income_amount = random.randint(0, 500000)
        income_description = 'test income'
        test_id = self.test_users[0]['chat_id']
        initial_balance = self.db.get_balance(test_id)
        new_balance = self.db.add_income(test_id, income_amount, income_description)
        self.assertEqual(new_balance, self.db.get_balance(test_id))
        self.assertEqual(new_balance, initial_balance + income_amount)

    def test_add_outcome(self):
        outcome_amount = random.randint(0, 50000)
        outcome_description = 'test_outcome'
        test_id = self.test_users[0]['chat_id']
        initial_balance = self.db.get_balance(test_id)
        new_balance = self.db.add_outcome(test_id, outcome_amount, outcome_description)
        self.assertEqual(new_balance, self.db.get_balance(test_id))
        self.assertEqual(new_balance, initial_balance - outcome_amount)

    def test_del_last_transaction(self):
        test_id = self.test_users[0]['chat_id']
        income_1 = {
            'amount': random.randint(0, 50000),
            'description': 'testing deleting last income 1',
            'date': date.today(),
        }
        income_2 = {
            'amount': random.randint(0, 50000),
            'description': 'testing deleting last income 2',
            'date': date.today(),
        } 
        self.db.add_income(test_id, income_1['amount'], income_1['description'])
        initial_balance = self.db.get_balance(test_id)
        self.db.add_income(test_id, income_2['amount'], income_2['description'])
        self.db.del_last_transaction(test_id)
        self.assertEqual(initial_balance, self.db.get_balance(test_id))
        self.assertFalse(income_2 in self.db.get_incomes(test_id))

    def test_get_incomes(self):
        test_id = self.test_users[0]['chat_id']
        incomes = [
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 1',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 2',
                'date': date.today()
            }
        ]
        for income in incomes:
            self.db.add_income(test_id, income['amount'], income['description'])
        self.assertEqual(self.db.get_incomes(test_id), incomes)

    def test_get_outcomes(self):
        test_id = self.test_users[0]['chat_id']
        outcomes = [
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 1',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 2',
                'date': date.today()
            }
        ]
        for outcome in outcomes:
            self.db.add_outcome(test_id, outcome['amount'], outcome['description'])
        self.assertEqual(self.db.get_outcomes(test_id), outcomes)

    def test_get_today_outcomes(self):
        test_id = self.test_users[0]['chat_id']
        outcomes = [
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 1',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 2',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 3',
                'date': date.today() - timedelta(days=1)
            }
        ]
        for outcome in outcomes:
            self.db._add_outcome_free_date(test_id, outcome['amount'], outcome['description'], outcome['date'])
        self.assertEqual(self.db.get_today_outcomes(test_id), outcomes[:-1])

    def test_get_outcomes_for_n_days(self):
        test_id = self.test_users[0]['chat_id']
        outcomes = [
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 1',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 2',
                'date': date.today()
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 3',
                'date': date.today() - timedelta(days=1)
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 4',
                'date': date.today() - timedelta(days=1)
            },
            {
                'amount': random.randint(0, 50000),
                'description': 'test income 5',
                'date': date.today() - timedelta(days=2)
            },
        ]
        r = {
            date.today(): outcomes[:2],
            date.today() - timedelta(days=1): outcomes[2:-1]
        }
        for outcome in outcomes:
            self.db._add_outcome_free_date(test_id, outcome['amount'], outcome['description'], outcome['date'])
        result = self.db.get_outcomes_for_n_days(test_id, 2)
        self.assertEqual(result, r)




if __name__ == '__main__':
    unittest.main()