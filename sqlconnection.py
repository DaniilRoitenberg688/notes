import sqlite3

from bcrypt import hashpw, gensalt


class SqlConnector:
    def __init__(self, db_name: str):
        self.db = db_name
        self.salt = gensalt()

    def user_by_id(self, user_id: int):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            user = cursor.execute(f'SELECT * FROM users WHERE id == {user_id}').fetchone()
            if not user:
                print('No user with such id')
                return False
            return user

        except Exception as e:
            print(e)
            return False

    def all_users(self):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            all_users = cursor.execute('SELECT * FROM users').fetchall()
            return all_users
        except Exception as e:
            print(e)
            return False

    def delete_user_by_id(self, user_id: int):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM users WHERE id == {user_id}')
            connection.commit()
        except Exception as e:
            print(e)
            return False

    def find_most_id(self, table):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            user_id = cursor.execute(f'SELECT id FROM {table} ORDER BY id DESC').fetchone()
            if user_id:
                return user_id[0]
            return -1

        except Exception as e:
            print(e)
            return False

    def add_new_user(self, user, password):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            hashed_password = hashpw(password.encode('utf-8'), gensalt())
            id = self.find_most_id('users') + 1
            cursor.execute(f'INSERT INTO users (id, login, password) VALUES ({id}, "{user}", "{hashed_password}")')
            connection.commit()
        except Exception as e:
            print(e)
            return False

    def select_users_by_login(self, login):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            user = cursor.execute(f'SELECT * FROM users WHERE login LIKE "{login}"').fetchone()
            if not user:
                print('No user with such login')
                return False
            return user
        except Exception as e:
            print(e)
            return False

    def all_notes(self, user_id=-1):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            if user_id == -1:
                notes = cursor.execute('SELECT * FROM notes').fetchall()
            else:
                notes = cursor.execute(f'SELECT * FROM notes WHERE user_id == {int(user_id)}').fetchall()
            if not notes:
                print('This user has no notes')
                return False
            return notes
        except Exception as e:
            print(e)
            return False

    def find_note(self, note_id):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            note = cursor.execute(f'SELECT * FROM notes WHERE id == {int(note_id)}').fetchone()
            if not note:
                print('No note with such id')
                return False
            return note
        except Exception as e:
            print(e)
            return False

    def delete_note(self, note_id):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM notes WHERE id == {note_id}')
            connection.commit()

        except Exception as e:
            print(e)
            return False

    def add_note(self, title, user_id: int):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            id = self.find_most_id('notes') + 1
            cursor.execute(
                f'INSERT INTO notes (id, title, user_id, file) VALUES ({id}, "{title}", "{user_id}", "{str(id)}.txt")')
            connection.commit()
        except Exception as e:
            print(e)
            return False


    def edit_note(self, note_id, new_title):
        try:
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            cursor.execute(
                f'UPDATE notes SET title = "{new_title}" WHERE id == {note_id}')
            connection.commit()
        except Exception as e:
            print(e)
            return False




if __name__ == '__main__':
    a = SqlConnector('notes.db')
    a.edit_note(6, new_title='g')