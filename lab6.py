from flask import Blueprint, render_template, request, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

@lab6.route('/lab6/')
def lab():
    return render_template('lab6/lab6.html', current_user=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='sasha_denisenko_knowledge_base',
            user='sasha_denisenko_knowledge_base',
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

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    # Получаем JSON-данные из запроса
    data = request.json
    # Извлекаем идентификатор запроса для соответствия JSON-RPC спецификации
    id = data['id']
    
    # Метод 'info' - возвращает информацию о всех офисах (доступен без авторизации)
    if data['method'] == 'info':
        conn, cur = db_connect()
        cur.execute("SELECT * FROM offices ORDER BY number;")
        offices = cur.fetchall()
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }

    # Проверяем авторизацию пользователя для остальных методов
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }
    
    # Метод 'booking' - бронирование офиса
    if data['method'] == 'booking':
        office_number = data['params'] # Получаем номер офиса из параметров запроса
        
        conn, cur = db_connect()

        # Выполняем параметризованный запрос для поиска офиса по номеру
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute("SELECT * FROM offices WHERE number = ?;", (office_number,))
        
        # Получаем первую (и единственную) запись офиса или None, если не найдено
        office = cur.fetchone()
        
        # Проверяем, существует ли офис с таким номером
        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Office not found'
                },
                'id': id
            }
        
        # Проверяем, не занят ли офис другим пользователем
        # Если поле tenant не пустое, значит офис уже забронирован
        if office['tenant'] != '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 2,
                    'message': 'Already booked'
                },
                'id': id
            }
        
        # Обновляем запись офиса, устанавливая текущего пользователя как арендатора
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", (login, office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", (login, office_number))
        
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'Booking successful',
            'id': id
        }
    
    # Метод 'cancellation' - отмена бронирования
    if data['method'] == 'cancellation':
        office_number = data['params']
        
        conn, cur = db_connect()
        
        # Ищем офис в базе данных
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute("SELECT * FROM offices WHERE number = ?;", (office_number,))
        
        # Получаем запись офиса
        office = cur.fetchone()
        
        # Проверяем существование офиса
        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Office not found'
                },
                'id': id
            }
        
        # Проверяем, что отменить бронирование может только тот пользователь,
        # который его создал (арендатор должен совпадать с текущим пользователем)
        if office['tenant'] != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Cannot cancel another user\'s booking'
                },
                'id': id
            }
        
        # Освобождаем офис, очищая поле tenant (устанавливаем пустую строку)
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = '' WHERE number = %s;", (office_number,))
        else:
            cur.execute("UPDATE offices SET tenant = '' WHERE number = ?;", (office_number,))
        
        db_close(conn, cur)
        
        # Возвращаем успешный результат
        return {
            'jsonrpc': '2.0',
            'result': 'Cancellation successful',
            'id': id
        }
    
    # Если передан неизвестный метод
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }