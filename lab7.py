from flask import Blueprint, render_template, request, abort, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

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

def validate_film(film):
    errors = {}

    title = film.get('title', '').strip()
    title_ru = film.get('title_ru', '').strip()
    description = film.get('description', '').strip()
    year_raw = film.get('year')

    if title_ru == '':
        errors['title_ru'] = 'Заполните название на русском'

    if title == '' and title_ru == '':
        errors['title'] = 'Заполните оригинальное название или название на русском'

    if title == '' and title_ru != '':
        film['title'] = title_ru

    if description == '':
        errors['description'] = 'Заполните описание'
    elif len(description) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    else:
        film['description'] = description

    try:
        year = int(year_raw)
        current_year = datetime.now().year
        if year < 1895 or year > current_year:
            errors['year'] = f'Год должен быть от 1895 до {current_year}'
        else:
            film['year'] = year
    except ValueError:
        errors['year'] = 'Заполните год'

    return errors

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()

    # Берем все фильмы, отсортированные по ID
    cur.execute("SELECT * FROM films ORDER BY id")
    films = cur.fetchall()

    db_close(conn, cur)

    # Преобразуем RealDictCursor объекты в список словарей
    return [dict(film) for film in films]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    
    # Ищем по ID (Primary Key)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT * FROM films WHERE id = ?", (id,))
        
    film = cur.fetchone()
    db_close(conn, cur)
    
    if film is None:
        abort(404)
        
    return dict(film)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    
    # Удаляем по ID
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM films WHERE id = %s", (id,))
    else:
        cur.execute("DELETE FROM films WHERE id = ?", (id,))
        
    db_close(conn, cur)
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film_data = request.get_json()

    errors = validate_film(film_data)
    if errors:
        return errors, 400

    conn, cur = db_connect()

    # Обновляем существующую запись по её первичному ключу (id)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE films 
            SET title = %s, title_ru = %s, year = %s, description = %s
            WHERE id = %s
            RETURNING *
        """, (film_data['title'], film_data['title_ru'], film_data['year'], film_data['description'], id))
        updated_film = cur.fetchone()
    else:
        cur.execute("""
            UPDATE films 
            SET title = ?, title_ru = ?, year = ?, description = ?
            WHERE id = ?
        """, (film_data['title'], film_data['title_ru'], film_data['year'], film_data['description'], id))
        conn.commit()
        # Повторно читаем запись, чтобы вернуть актуальные данные
        cur.execute("SELECT * FROM films WHERE id = ?", (id,))
        updated_film = cur.fetchone()

    db_close(conn, cur)

    # Если запись с таким id не найдена или не обновилась - возвращаем 404 Not Found
    if updated_film is None:
        abort(404)

    # Преобразуем объект строки в обычный словарь и возвращаем как JSON-ответ
    return dict(updated_film)

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    # Получаем данные фильма из тела HTTP‑запроса в формате JSON
    film_data = request.get_json()

    # Проверяем на ошибки
    errors = validate_film(film_data)
    if errors:
        return errors, 400

    conn, cur = db_connect()
    
    # Вставляем новую запись в таблицу films
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            INSERT INTO films (title, title_ru, year, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (film_data['title'], film_data['title_ru'], film_data['year'], film_data['description']))
        new_id = cur.fetchone()['id']
    else:
        cur.execute("""
            INSERT INTO films (title, title_ru, year, description)
            VALUES (?, ?, ?, ?)
        """, (film_data['title'], film_data['title_ru'], film_data['year'], film_data['description']))
        new_id = cur.lastrowid
       
    db_close(conn, cur)
    
    # Возвращаем ID созданного фильма и статус 201 (Created)
    return {"id": new_id}, 201
