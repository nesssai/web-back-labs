from flask import Blueprint, render_template, request, redirect, url_for, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from os import path
import re

rgz = Blueprint('rgz', __name__)

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='sasha_denisenko_storage_system',
            user='sasha_denisenko_storage_system',
            password='sasha12'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

# Валидация логина
def validate_login(login):
    if not login or len(login) < 3 or len(login) > 30:
        return False
    pattern = r'^[a-zA-Z0-9._-]+$'
    return bool(re.match(pattern, login))

# Валидация пароля
def validate_password(password):
    if not password or len(password) < 5:
        return False
    pattern = r'^[a-zA-Z0-9!@#$%^&*()_+=\-\[\]{};:,.<>?]+$'
    return bool(re.match(pattern, password))

@rgz.route('/rgz/')
def main():
    """Главная страница - отображение камеры хранения"""
    conn, cur = db_connect()
    
    # Получаем все ячейки с информацией о пользователях
    cur.execute("""
        SELECT c.id, c.cell_number, c.user_id, c.booked_at, u.login
        FROM cells c
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.cell_number
    """)
    cells = cur.fetchall()
    
    # Подсчет свободных и занятых ячеек
    free_count = sum(1 for cell in cells if cell['user_id'] is None)
    occupied_count = len(cells) - free_count
    
    # Если пользователь авторизован, получаем его забронированные ячейки
    user_booked_count = 0
    if 'user_id' in session:
        user_booked_count = sum(1 for cell in cells if cell['user_id'] == session['user_id'])
    
    db_close(conn, cur)
    
    return render_template('rgz/index.html', 
                         cells=cells, 
                         free_count=free_count,
                         occupied_count=occupied_count,
                         user_booked_count=user_booked_count,
                         login=session.get('login'))

@rgz.route('/rgz/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if request.method == 'GET':
        return render_template('rgz/register.html')
    
    login = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()
    password_confirm = request.form.get('password_confirm', '').strip()
    
    # Валидация
    if not (login and password and password_confirm):
        return render_template('rgz/register.html', 
                             error='Заполните все поля', 
                             login=login)
    
    if not validate_login(login):
        return render_template('rgz/register.html', 
                             error='Логин должен содержать 3-30 символов (латинские буквы, цифры, точка, дефис, подчеркивание)',
                             login=login)
    
    if not validate_password(password):
        return render_template('rgz/register.html', 
                             error='Пароль должен содержать минимум 5 символов',
                             login=login)
    
    if password != password_confirm:
        return render_template('rgz/register.html', 
                             error='Пароли не совпадают',
                             login=login)
    
    conn, cur = db_connect()
    
    # Проверка существования пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login = %s", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login = ?", (login,))
    
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('rgz/register.html', 
                             error='Пользователь с таким логином уже существует',
                             login=login)
    
    # Хеширование пароля с солью
    password_hash = generate_password_hash(password)
    
    # Сохранение пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password) VALUES (%s, %s) RETURNING id", 
                    (login, password_hash))
        user_id = cur.fetchone()['id']
    else:
        cur.execute("INSERT INTO users (login, password) VALUES (?, ?)", 
                    (login, password_hash))
        user_id = cur.lastrowid
    
    db_close(conn, cur)
    
    # Автоматическая авторизация после регистрации
    session['user_id'] = user_id
    session['login'] = login
    
    return render_template('rgz/success.html', 
                         message='Регистрация прошла успешно!',
                         login=login)

@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    """Авторизация пользователя"""
    if request.method == 'GET':
        return render_template('rgz/login.html')
    
    login_input = request.form.get('login', '').strip()
    password = request.form.get('password', '').strip()
    
    if not (login_input and password):
        return render_template('rgz/login.html', 
                             error='Заполните все поля')
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, login, password FROM users WHERE login = %s", 
                    (login_input,))
    else:
        cur.execute("SELECT id, login, password FROM users WHERE login = ?", 
                    (login_input,))
    
    user = cur.fetchone()
    
    db_close(conn, cur)
    
    if not user or not check_password_hash(user['password'], password):
        return render_template('rgz/login.html', 
                             error='Неверный логин или пароль')
    
    # Сохранение в сессии
    session['user_id'] = user['id']
    session['login'] = user['login']
    
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/logout', methods=['POST'])
def logout():
    """Выход из системы"""
    session.pop('user_id', None)
    session.pop('login', None)
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/book/<int:cell_number>', methods=['POST'])
def book_cell(cell_number):
    """Бронирование ячейки"""
    # Проверка авторизации
    if 'user_id' not in session:
        return redirect(url_for('rgz.login'))
    
    user_id = session['user_id']
    
    conn, cur = db_connect()
    
    # Проверка количества уже забронированных ячеек
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT COUNT(*) as count FROM cells WHERE user_id = %s", (user_id,))
    else:
        cur.execute("SELECT COUNT(*) as count FROM cells WHERE user_id = ?", (user_id,))
    
    booked_count = cur.fetchone()['count']
    
    if booked_count >= 5:
        db_close(conn, cur)
        session['error_message'] = 'Вы уже забронировали максимальное количество ячеек (5)'
        return redirect(url_for('rgz.main'))
    
    # Проверка доступности ячейки
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT user_id FROM cells WHERE cell_number = %s", (cell_number,))
    else:
        cur.execute("SELECT user_id FROM cells WHERE cell_number = ?", (cell_number,))
    
    cell = cur.fetchone()
    
    if cell and cell['user_id'] is not None:
        db_close(conn, cur)
        return redirect(url_for('rgz.main'))
    
    # Бронирование ячейки
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE cells 
            SET user_id = %s, booked_at = CURRENT_TIMESTAMP 
            WHERE cell_number = %s AND user_id IS NULL
        """, (user_id, cell_number))
    else:
        cur.execute("""
            UPDATE cells 
            SET user_id = ?, booked_at = CURRENT_TIMESTAMP 
            WHERE cell_number = ? AND user_id IS NULL
        """, (user_id, cell_number))
    
    db_close(conn, cur)
    
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/release/<int:cell_number>', methods=['POST'])
def release_cell(cell_number):
    """Снятие брони с ячейки"""
    # Проверка авторизации
    if 'user_id' not in session:
        return redirect(url_for('rgz.login'))
    
    user_id = session['user_id']
    
    conn, cur = db_connect()
    
    # Снятие брони (только если ячейка принадлежит пользователю)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE cells 
            SET user_id = NULL, booked_at = NULL 
            WHERE cell_number = %s AND user_id = %s
        """, (cell_number, user_id))
    else:
        cur.execute("""
            UPDATE cells 
            SET user_id = NULL, booked_at = NULL 
            WHERE cell_number = ? AND user_id = ?
        """, (cell_number, user_id))
    
    db_close(conn, cur)
    
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/delete-account', methods=['POST'])
def delete_account():
    """Удаление аккаунта пользователя"""
    if 'user_id' not in session:
        return redirect(url_for('rgz.main'))
    
    user_id = session['user_id']
    
    conn, cur = db_connect()
    
    # Освобождение всех ячеек пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE cells SET user_id = NULL, booked_at = NULL WHERE user_id = %s", 
                    (user_id,))
        # Удаление пользователя
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    else:
        cur.execute("UPDATE cells SET user_id = NULL, booked_at = NULL WHERE user_id = ?", 
                    (user_id,))
        # Удаление пользователя
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    db_close(conn, cur)
    
    # Выход из системы
    session.clear()
    
    return redirect(url_for('rgz.main'))