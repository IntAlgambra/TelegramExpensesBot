import unittest
from datetime import date, timedelta

from backend import Backend
from database import Database

class TestBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database()
        cls.backend = Backend()
        cls.test_id = 132435
        cls.test_balance = 100000

    def setUp(self):
        self.db.update_all()

    def test_create_account(self):
        self.backend.create_account(self.test_id, self.test_balance)
        self.assertTrue(self.db.check_user(self.test_id))

    def test_standart_outcome(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = '500 Lorem ipsum'
        outcome = {
            'amount': 500,
            'description': 'Lorem ipsum',
            'date': date.today(),
        }
        result = self.backend.process_transaction(self.test_id, message)
        self.assertEqual(result, 99500)
        self.assertTrue(outcome in self.db.get_outcomes(self.test_id))

    def test_outcome_with_minus(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = '-500 Lorem ipsum'
        outcome = {
            'amount': 500,
            'description': 'Lorem ipsum',
            'date': date.today(),
        }
        result = self.backend.process_transaction(self.test_id, message)
        self.assertEqual(result, 99500)
        self.assertTrue(outcome in self.db.get_outcomes(self.test_id))

    def test_standart_income(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = '+500 Lorem ipsum'
        income = {
            'amount': 500,
            'description': 'Lorem ipsum',
            'date': date.today(),
        }
        result = self.backend.process_transaction(self.test_id, message)
        self.assertEqual(result, 100500)
        self.assertTrue(income in self.db.get_incomes(self.test_id))

    def test_income_without_description(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = '+500'
        income = {
            'amount': 500,
            'description': 'circumstances of this outcome is unclear',
            'date': date.today(),
        }
        result = self.backend.process_transaction(self.test_id, message)
        self.assertEqual(result, 100500)
        self.assertTrue(income in self.db.get_incomes(self.test_id))

    def test_outcome_without_description(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = '500'
        outcome = {
            'amount': 500,
            'description': 'circumstances of this outcome is unclear',
            'date': date.today(),
        }
        result = self.backend.process_transaction(self.test_id, message)
        self.assertEqual(result, 99500)
        self.assertTrue(outcome in self.db.get_outcomes(self.test_id))

    def test_incorrect_transaction(self):
        self.backend.create_account(self.test_id, self.test_balance)
        message = 'kk[cscc;v]vmpsvssc ksmc spdcsd  cc '
        result = self.backend.process_transaction(self.test_id, message)
        self.assertIsNone(result)

    def test_update_balance(self):
        new_balance = 20000
        self.backend.create_account(self.test_id, self.test_balance)
        result = self.backend.update_balance(self.test_id, new_balance)
        self.assertEqual(self.db.get_balance(self.test_id), new_balance)
        self.assertEqual(result, new_balance)

    def test_get_balance(self):
        self.backend.create_account(self.test_id, self.test_balance)
        self.assertEqual(self.backend.get_balance(self.test_id), self.test_balance)

    def test_get_today_outcomes(self):
        self.backend.create_account(self.test_id, self.test_balance)
        messages = [
            '500 food',
            '300 some userful staff',
            '400 lol kek',
        ]
        for message in messages:
            self.backend.process_transaction(self.test_id, message)
        result = self.backend.get_today_outcomes(self.test_id)
        self.assertIsNotNone(result)


    def test_get_outcomes_for_n_days(self):
        self.backend.create_account(self.test_id, self.test_balance)
        messages = {
            date.today(): '500 food',
            date.today() - timedelta(days=1): '300 some stuff',
            date.today() - timedelta(days=3): '4000 more stuff'
        }
        for day in messages:
            self.backend._process_transaction_with_day(self.test_id, messages[day], day)
        result = self.backend.get_outcomes_for_n_days(self.test_id, 2)
        self.assertIsNotNone(result)

    def test_get_csv_outcomes(self):
        self.backend.create_account(self.test_id, self.test_balance)
        messages = {
            date.today(): '500 food',
            date.today() - timedelta(days=1): '300 some stuff',
            date.today() - timedelta(days=3): '4000 more stuff'
        }
        for day in messages:
            self.backend._process_transaction_with_day(self.test_id, messages[day], day)
        csv_file = self.backend.get_csv_outcomes(self.test_id)
        csv_file.close()
        self.assertIsNotNone(csv_file)


if __name__ == '__main__':
    unittest.main()