'''
структура базы данных бота:

-Таблица "users" с записями:
    -id
    -balance
    -outcomes foreign key на таблицу расходов
    -incomes foreign key на таблицу доходов

-Таблица расходов

    -id primary key
    -amount
    -description

-Таблица доходов аналогична таблице расходов

API доступа к базе данных

-add_user(chat_id, balance) - добавить пользователя с изначальным балансом
-get_balance(chat_id) - получить баланс пользоввателя, возвращает баланс
-update_balance(chat_id, balance) - обновить баланс пользователя, возвращщает баланс
-add_income(chat_id, amount, description) - добавить доход, возвращает баланс
-add_outcome(chat_id, amount, description) - добавляет расход, возвращает баланс
-get_incomes(chat_id) - возвращает доходы пользователя в виде словаря с полями дата. сумма и описание
-get outcomes(chat_id) - возвращает расходы пользователей
'''
import os

from datetime import date, timedelta

from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine, event
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.exc import IntegrityError, OperationalError

from sqlalchemy.orm.exc import UnmappedInstanceError

from sqlalchemy.engine import Engine

#Обработчик для автоматического включения внешних ключей в sqlite3
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

#имя файла с базой sqlite
DATABASE_FILENAME = 'users'

#Создаем родительский класс для всех таблиц в базе данных
DB = declarative_base()

#Таблица с данными о клиентах
class Users(DB):

    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, unique = True)
    balance = Column(Integer)

class Outcomes(DB):

    __tablename__ = 'outcomes'

    oid = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('users.user_id', onupdate = "CASCADE", ondelete = "CASCADE"))
    amount = Column(Integer)
    description = Column(String)
    date = Column(Date)

    def dict_outcome(self):
        result = {
            'amount': self.amount,
            'description': self.description,
            'date': self.date
        }
        return result

class Incomes(DB):

    __tablename__ = 'incomes'

    iid = Column(Integer, primary_key = True, autoincrement = True)
    user_id = Column(Integer, ForeignKey('users.user_id', onupdate = "CASCADE", ondelete = "CASCADE"))
    amount = Column(Integer)
    description = Column(String)
    date = Column(Date)

    def dict_income(self):
        result = {
            'amount': self.amount,
            'description': self.description,
            'date': self.date
        }
        return result

class Database():

    def __init__(self, filename = DATABASE_FILENAME):
        self.database = DB
        self.filename = filename
        self.last_transaction_type = None
        #check if database was created
        is_database_exist = os.path.isfile(self.filename)
        self.engine = create_engine('sqlite:///{}.db'.format(self.filename))
        if not is_database_exist:
            self.database.metadata.create_all(self.engine)
        self.session_factory = sessionmaker(bind = self.engine)
        self.session = scoped_session(self.session_factory)

    def update_all(self):
        self.database.metadata.drop_all(self.engine)
        self.database.metadata.create_all(self.engine)
 
    def decorate(func):
        '''
        Этот декоратор обеспечивает работу открытие и закрытие сессии
        для каждой операции с БД
        '''
        def wrapper(*args, **kwargs):
            object_instance = args[0] #это self
            # args = args[1:]
            session = object_instance.session()
            args = list(args)
            args.append(session)
            try:
                return func(*args)
            except Exception as e:
                print(e)
                session.rollback()
            finally:
                object_instance.session.remove()

        return wrapper

    @decorate
    def add_user(self, chat_id, balance, *args):
        user = Users(chat_id = chat_id, balance = balance)
        session = args[0]
        session.add(user)
        session.commit()

    @decorate
    def get_balance(self, chat_id, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        balance = user.balance
        return balance

    @decorate
    def update_balance(self, chat_id, new_balanace, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        user.balance = new_balanace
        session.commit()
        return new_balanace

    @decorate
    def add_income(self, chat_id, amount, description, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        if not description:
            description = 'circumstances of this outcome is unclear'
        income = Incomes(
            user_id = user.user_id,
            amount = amount,
            description = description,
            date = date.today()
        )
        user.balance += amount
        session.add(income)
        session.commit()
        self.last_transaction_type = 'income'
        return user.balance

    @decorate
    def add_outcome(self, chat_id, amount, description, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        if not description:
            description = 'circumstances of this outcome is unclear'
        outcome = Outcomes(
            user_id = user.user_id,
            amount = amount,
            description = description,
            date = date.today()
        )
        user.balance -= amount
        session.add(outcome)
        session.commit()
        self.last_transaction_type = 'outcome'
        return user.balance

    @decorate
    def _add_outcome_free_date(self, chat_id, amount, description, free_date, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        if not description:
            description = 'circumstances of this outcome is unclear'
        outcome = Outcomes(
            user_id = user.user_id,
            amount = amount,
            description = description,
            date = free_date
        )
        user.balance -= amount
        session.add(outcome)
        session.commit()
        self.last_transaction_type = 'outcome'
        return user.balance

    @decorate
    def del_last_transaction(self, chat_id, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        user_id = user.user_id
        if self.last_transaction_type == 'income':
            income = (session.query(Incomes).filter(Incomes.user_id == user_id).order_by(-Incomes.iid).first())
            amount = income.amount
            user.balance -= amount
            session.delete(income)
            session.commit()
            self.last_transaction_type = None
            return user.balance
        elif self.last_transaction_type == 'outcome':
            outcome = (session.query(Outcomes).filter(Outcomes.user_id == user_id).order_by(-Outcomes.iid).first())
            amount = outcome.amount
            user.balance += amount
            session.delete(outcome)
            self.last_transaction_type = None
            session.commit()
            return user.balance
        else:
            return None


    @decorate
    def get_incomes(self, chat_id, *args):
        session = args[0]
        user_id = session.query(Users).filter(Users.chat_id == chat_id).first().user_id
        incomes_query = session.query(Incomes).filter(Incomes.user_id == user_id).all()
        if incomes_query:
            incomes = [income.dict_income() for income in incomes_query]
        else:
            incomes = []
        return incomes

    @decorate
    def get_outcomes(self, chat_id, *args):
        session = args[0]
        user_id = session.query(Users).filter(Users.chat_id == chat_id).first().user_id
        outcomes_query = session.query(Outcomes).filter(Outcomes.user_id == user_id).all()
        outcomes = [outcome.dict_outcome() for outcome in outcomes_query]
        return outcomes

    @decorate
    def get_today_outcomes(self, chat_id, *args):
        session = args[0]
        user_id = session.query(Users).filter(Users.chat_id == chat_id).first().user_id
        outcomes_query = (
            session.query(Outcomes).filter(Outcomes.user_id == user_id).filter(Outcomes.date == date.today()).all()
        )
        outcomes = [outcome.dict_outcome() for outcome in outcomes_query]
        return outcomes

    @decorate
    def get_outcomes_for_n_days(self, chat_id, days, *args):
        session = args[0]
        user_id = session.query(Users).filter(Users.chat_id == chat_id).first().user_id
        outcomes = {}
        for day in range(days):
            day_outcomes_query = (
                session.query(Outcomes).filter(Outcomes.user_id == user_id).filter(Outcomes.date ==     (date.today() - timedelta(days=day))).all()
            )
            day_outcomes = [outcome.dict_outcome() for outcome in day_outcomes_query]
            outcomes[(date.today() - timedelta(days=day))] = day_outcomes
        return outcomes

    @decorate
    def get_week_outcomes(self, chat_id, *args):
        pass

    @decorate
    def check_user(self, chat_id, *args):
        session = args[0]
        user = session.query(Users).filter(Users.chat_id == chat_id).first()
        if user:
            return True
        return False



if __name__ == '__main__':
    database = Database(filename='test')
    database.update_all()
    test_users = [
            {
                'chat_id': 123456,
                'balance': 100000,
            },
        ]
    for user in test_users:
       database.add_user(user['chat_id'], user['balance'])

