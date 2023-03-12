import psycopg2
from psycopg2 import Error
import sys

from parsing import codeforces_parser


class PostgreSQL(object):

    def __init__(self):
        """ Инициализатор для определения атрибутов БД """
        self.hostname = 'localhost'
        self.username = 'postgres'
        self.password = 'admin'
        self.database = 'postgres'
        self.port = '5433'
        print("Database opened successfully")

        ''' Соединяемся с БД, определяем connect и cursor '''
        try:
            self.connect = psycopg2.connect(
                dbname=self.database,
                user=self.username,
                password=self.password,
                host=self.hostname,
                port="5433")
            self.cursor = self.connect.cursor()
            print('connect successfully')

        except psycopg2.Error:
            error = 'Failed to setup Postgres environment.\n{0}'.format(sys.exc_info())
            print('Ошибка подключения к базе данных' + '\ n' + error)

        """ Создание таблицы tasks, для хранения номера задачи, названия, ложности и кол-ва решений """

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TASKS
        (NUMBER VARCHAR(50) NOT NULL PRIMARY KEY,
        NAME VARCHAR(100) NOT NULL,
        COMPLEXITY INT,
        "DECISIONS NUMBER" INT);''')
        self.connect.commit()
        print("table is create")

        ''' Создание таблицы topics, для хранения номера задачи, темы (для одного и того же номера могут
        быть несколько тем, для этого создаем 2 связанные таблицы) '''

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TOPICS
        (NUMBER VARCHAR(50) REFERENCES TASKS(NUMBER),
        TOPIC VARCHAR(100));''')
        self.connect.commit()

    ############################################################### end def __init__

    def insert_topics(self, number, topic):
        """ Заполнение таблицы topics данными """
        try:
            self.cursor.execute('''INSERT INTO TOPICS(NUMBER, TOPIC) VALUES (%s,%s) ON CONFLICT DO NOTHING''',
                                (number, topic))
            self.connect.commit()
        except (Exception, Error) as error:
            print('Ошибка сохранения: ', error, 'Значения: ', (number, topic))
            pass

    def insert_tasks(self, number, name, complexity, decisions_number):
        """ Заполнение таблицы tasks данными """
        try:
            self.cursor.execute(
                '''INSERT INTO TASKS(NUMBER, NAME, COMPLEXITY, "DECISIONS NUMBER") 
                VALUES (%s,%s,%s,%s) ON CONFLICT(NUMBER) DO NOTHING''', (number, name, complexity, decisions_number))
            self.connect.commit()
        except (Exception, Error) as error:
            print('Ошибка сохранения: ', error, 'Значения: ', (number, name, complexity, decisions_number))
            pass

    def execute_read_query(self, connection, query, parametrs=None):
        """Исполнение написанных select"""
        result = None
        try:
            self.cursor.execute(query, parametrs)
            result = self.cursor.fetchall()
            return result
        except (Exception, Error) as error:
            print(f"The error '{error}' occurred")

    def select_data(self):
        """ Получение данных в обработанном формате (после JOIN двух связанных таблиц) """

        select_join = '''SELECT TOPICS.NUMBER, TOPICS.TOPIC, TASKS.NAME, TASKS.COMPLEXITY, TASKS."DECISIONS NUMBER"
                FROM TOPICS 
                INNER JOIN TASKS 
                ON TASKS.NUMBER = TOPICS.NUMBER; '''

        return self.execute_read_query(self.connect, select_join, ())

    def get_search(self, topic, complexity):
        """Поиск(уникальный) по конкретным темам+сложностям"""
        select = f'''SELECT DISTINCT TOPICS.NUMBER, TASKS.NAME, TOPICS.TOPIC, TASKS.COMPLEXITY, TASKS."DECISIONS NUMBER"
                        FROM TOPICS 
                        INNER JOIN TASKS 
                        ON TASKS.NUMBER = TOPICS.NUMBER
                        WHERE (TOPICS.TOPIC = %s
                        AND TASKS.COMPLEXITY = %s)
                        LIMIT 10;'''
        print('ТУТ наши переменные!!!! ', topic, complexity)
        return self.execute_read_query(self.connect, select, (topic, complexity))

    def get_topics(self):
        """Получение списка тем"""
        select = '''SELECT DISTINCT TOPIC
                        FROM TOPICS;'''
        return self.execute_read_query(self.connect, select)

    def get_complex(self):
        """Получение списка тем"""
        select = '''SELECT DISTINCT COMPLEXITY
                        FROM TASKS;'''
        return self.execute_read_query(self.connect, select)

def check():
    print('Проверка check')
    """Парсинг каждый час"""
    db = PostgreSQL()

    for page in range(1, 87):
        print(f'{page}-я страница')
        URL_TEMPLATE = f"https://codeforces.com/problemset/page/{page}?order=BY_SOLVED_DESC"
        headers = {'Accept-Language': 'ru-RU'}
        main_data, topics_data = codeforces_parser(URL_TEMPLATE=URL_TEMPLATE, headers=headers)

        for row in main_data.itertuples(index=False):
            db.insert_tasks(row[0], row[1], row[2], row[3])

        for row in topics_data.itertuples(index=False):
            db.insert_topics(row[0], row[1])
    db.connect.close()
