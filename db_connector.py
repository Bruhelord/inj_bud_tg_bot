import sqlite3
import datetime


COMMAND_CREATE_TASK = "INSERT INTO tasks (text, status, date, chat_id, time) VALUES (?, ?, ?, ?, ?)"
COMMAND_CHANGE_TASK = "UPDATE tasks SET status = ?, time = ? WHERE text = ? AND chat_id = ?"
COMMAND_GET_TIME  = "SELECT date FROM tasks WHERE text = ? AND chat_id = ?"
COMMAND_TASK_CHECK = "SELECT * FROM tasks WHERE text = ? AND chat_id = ?"
COMMAND_STATUS_CHECK = "SELECT status FROM tasks WHERE text = ? AND chat_id = ?"
COMMAND_CLEAR_TASK = "DELETE FROM tasks WHERE text = ? AND chat_id = ?"
COMMAND_CLEAR_TASKS = "DELETE FROM tasks WHERE chat_id = ?"
COMMAND_GET_ALL = "SELECT text, status, date, chat_id, time FROM tasks WHERE chat_id = ?"



class DbConnector:
    """класс для подключения к бд"""
    def __init__(self, db_name):
        self.db_name = db_name

    def create_new_task(self, task, chat_id):
        """Добавляет задачу в бд"""
        now = datetime.datetime.now()
        formatted_time = f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}"
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        cursor.execute(COMMAND_CREATE_TASK, (task, '⬜', formatted_time, chat_id, ''))
        sqlite_connection.commit()
        sqlite_connection.close()

    def check_task(self, task, chat_id):
        """Проверяет наличие задачи в бд"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        info = cursor.execute(COMMAND_TASK_CHECK, (task, chat_id))
        if info.fetchone() is None:
            sqlite_connection.close()
            return False
        sqlite_connection.close()
        return True

    def change_task(self, task, chat_id):
        """Изменяет задачу в бд"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        status = cursor.execute(COMMAND_STATUS_CHECK, (task, chat_id)).fetchone()
        status = status[0]
        if status == '⬜':
            cursor.execute(COMMAND_CHANGE_TASK, ('❌', '', task, chat_id,))
        elif status == '❌' or status == '✅':
            cursor.execute(COMMAND_CHANGE_TASK, ('⬜', "", task, chat_id,))
        sqlite_connection.commit()
        sqlite_connection.close()

    def clear_task(self, task, chat_id):
        """Удаляет выбранную задачу в бд"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        cursor.execute(COMMAND_CLEAR_TASK, (task, chat_id))
        sqlite_connection.commit()
        sqlite_connection.close()



    def clear_tasks(self, chat_id):
        """Удаляет все задачи в бд"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        cursor.execute(COMMAND_CLEAR_TASKS, (chat_id, ))
        sqlite_connection.commit()
        sqlite_connection.close()

    def complete_task(self, task, chat_id):
        """Изменяет статус задачи на 'завершено'"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        status = cursor.execute(COMMAND_STATUS_CHECK, (task, chat_id)).fetchone()
        status = status[0]
        if status == '⬜' or status == '❌':
            now = datetime.datetime.now()
            date2  = datetime.datetime(now.year,
                                       now.month,
                                       now.day,
                                       now.hour,
                                       now.minute,
                                       now.second)
            temp = cursor.execute(COMMAND_GET_TIME, (task, chat_id)).fetchone()[0]
            temp2 = map(int, temp.split('_'))
            date1 = datetime.datetime(*temp2)
            diff = date2 - date1
            cursor.execute(COMMAND_CHANGE_TASK,
            ('✅', f"{diff.days}_{diff.seconds // 3600}_{(diff.seconds // 60) % 60}", task, chat_id))
        sqlite_connection.commit()
        sqlite_connection.close()

    def get_all_tasks(self, chat_id):
        """Выдает список со всеми задачами"""
        sqlite_connection = sqlite3.connect(self.db_name)
        cursor = sqlite_connection.cursor()
        tasks = cursor.execute(COMMAND_GET_ALL, (chat_id,)).fetchall()
        sqlite_connection.close()
        return tasks
