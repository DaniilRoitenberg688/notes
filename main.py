import os
from crypt import methods
from pyexpat.errors import messages

from sqlconnection import SqlConnector
from flask import Flask, render_template, session, request, redirect, flash
from bcrypt import checkpw


app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

sql_base = SqlConnector('notes.db')

@app.route('/')
def index():
    if session['auth']:
        user_id, user_login, _ = sql_base.user_by_id(session.get('user_id'))
        notes = sql_base.all_notes(user_id)
        if notes:
            notes = [list(i) for i in sql_base.all_notes(user_id)]
        else:
            notes = []

        for note in notes:
            with open(f'notes_texts/{note[3]}') as file:
                note[3] = file.read()

        return render_template('index.html', title='Заметки', is_auth=True, user_login=user_login,
                               notes=notes)

    return render_template('login.html', title='Вход')

@app.route('/login', methods=['get', 'post'])
def login():
    user_login = request.form.get('login')
    user = sql_base.select_users_by_login(user_login)
    if not user:
        return render_template('login.html', title='Вход', message='Нет такого пользователя',
                               login=user_login)

    password = request.form.get('password')
    user_password: str = user[2][2:-1]
    password = password.encode('utf-8')
    a = checkpw(password, user_password.encode('utf-8'))
    if not a:
        return render_template('login.html', title='Вход', message='Неверный пароль',
                               login=user_login)

    session['auth'] = True
    session['user_id'] = user[0]
    return redirect('/')

@app.route('/logout')
def logout():
    session['auth'] = False
    return redirect('/')


@app.route('/register_form')
def register_form():
    return render_template('registration.html',
                           tilte='Регистрация')

@app.route('/register', methods=['post', 'get'])
def register():
    user_login: str = request.form.get('login', -1)
    if user_login == -1:
        return render_template('registration.html', message='Введите логин',
                               tilte='Регистрация', login=user_login)

    if sql_base.select_users_by_login(user_login):
        return render_template('registration.html', message='Пользователь с таким логином уже есть',
                               tilte='Регистрация', login=user_login)

    password = request.form.get('password', -1)
    password_again = request.form.get('password_again', -1)

    if password_again == -1 or password == -1:
        return render_template('registration.html', message='Введите пароль',
                               tilte='Регистрация', login=user_login)

    if password_again != password:

        return render_template('registration.html', message='Пароли не совпадают',
                               tilte='Регистрация', login=user_login)

    sql_base.add_new_user(user_login, password)



    return redirect('/')


@app.route('/add_note_form')
def add_note_form():
    return render_template('add_note.html', title='Добавление заметки')


@app.route('/add_note', methods=['get', 'post'])
def add_note():
    note_name = request.form.get('note_name', False)
    note_text = request.form.get('note_text', False)
    if not note_name:
        return render_template('add_note.html', title='Добавление заметки',
                               message='Укажите название заметки', note_text=note_text)

    if not note_text:
        return render_template('add_note.html', title='Добавление заметки',
                               message='Укажите текст заметки', note_name=note_name)

    last_num = sql_base.find_most_id('notes') + 1
    sql_base.add_note(title=note_name, user_id=int(session.get('user_id')))
    with open(f'notes_texts/{last_num}.txt', 'w') as file:
        file.write(note_text)

    return redirect('/')


@app.route('/delete_note/<note_id>')
def delete_note(note_id):
    note = sql_base.find_note(note_id)
    os.remove(f'notes_texts/{note[-1]}')
    sql_base.delete_note(note_id)
    return redirect('/')


@app.route('/edit_note_form/<note_id>')
def edit_note_form(note_id):
    note = sql_base.find_note(note_id)
    with open(f'notes_texts/{note[-1]}', 'r') as file:
        note_text = file.read()
    return render_template('edit_note.html', title='Изменение заметки', note_name=note[1],
                           note_text=note_text, note_id=note_id)

@app.route('/edit_note/<note_id>', methods=['post', 'get'])
def edit_note(note_id):
    note = sql_base.find_note(note_id)
    new_title = request.form.get('new_title', '')
    new_note_text = request.form.get('new_note_text', '')
    if not new_title:
        return render_template('edit_note.html', title='Изменение заметки', note_name=new_title,
                               note_text=new_note_text, note_id=note_id, message='Укажите название заметки')

    if not new_note_text:
        return render_template('edit_note.html', title='Изменение заметки', note_name=new_title,
                               note_text=new_note_text, note_id=note_id, message='Укажите текст заметки')

    sql_base.edit_note(note_id, new_title)

    with open(f'notes_texts/{note[-1]}', 'w') as file:
        file.write(new_note_text)

    return redirect('/')





if __name__ == '__main__':
    app.run(debug=True)