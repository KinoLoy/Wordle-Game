import os
import sqlite3


DATABASE = "settings.db"


class Database:

    def __init__(self):
        self._db = DATABASE
        if not os.path.exists(self._db):
            connection = sqlite3.connect(self._db)
            cursor = connection.cursor()
            cursor.execute("CREATE TABLE info(id integer, word_length integer, high_score integer)")
            cursor.execute('INSERT INTO info VALUES(?,?,?)', (0, 5, 0))
            connection.commit()
            connection.close()

    def _run_sql(self, sql):
        connection = sqlite3.connect(self._db)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        connection.close()

    def get_data(self):
        sql = "SELECT word_length, high_score FROM info WHERE id = 0"
        connection = sqlite3.connect(self._db)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchone()
        connection.close()
        return data["word_length"], data["high_score"]

    def set_data(self, word_length, high_score):
        sql = f"""
            UPDATE info
               SET word_length = {word_length}
                 , high_score = {high_score}
             WHERE id = 0
        """
        self._run_sql(sql)

    def set_high_score(self, high_score):
        sql = f"""
            UPDATE info
               SET high_score = {high_score}
             WHERE id = 0
        """
        self._run_sql(sql)
