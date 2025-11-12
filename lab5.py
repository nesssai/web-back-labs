from flask import Blueprint, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from os import path

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5/')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))

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

@lab5.route('/lab5/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    real_name = request.form.get('real_name')

    if not (login or password or real_name):
        return render_template('lab5/register.html', error='Заполните все поля')
    
    conn, cur =  db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT login FROM users WHERE login = ?;", (login,))

    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html', error="Такой пользователь уже существует")
    
    password_hash = generate_password_hash(password) # [cite: 302]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password, real_name) VALUES (%s, %s, %s);", (login, password_hash, real_name))
    else:
        cur.execute("INSERT INTO users (login, password, real_name) VALUES (?, ?, ?);", (login, password_hash, real_name))

    db_close(conn, cur)

    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')

    login = request.form.get('login')
    password = request.form.get('password')

    if not (login or password):
        return render_template('lab5/login.html', error="Заполните поля")
    
    conn, cur =  db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login, ))

    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')

    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html', error='Логин и/или пароль неверны')
    
    session['login'] = login
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login)

@lab5.route('/lab5/create', methods=['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')

    is_public = True if request.form.get('is_public') else False
    is_favorite = True if request.form.get('is_favorite') else False

    if not title or not article_text:
        error = "Заполните все поля!"
        return render_template('lab5/create_article.html', error=error, title=title, article_text=article_text)

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login, ))

    user_id = cur.fetchone()["id"]
        
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles(user_id, title, article_text, is_public, is_favorite) \
                      VALUES (%s, %s, %s, %s, %s);", (user_id, title, article_text, is_public, is_favorite))
    else:
        cur.execute("INSERT INTO articles(user_id, title, article_text, is_public, is_favorite) \
                      VALUES (?, ?, ?, ?, ?);", (user_id, title, article_text, is_public, is_favorite))

    db_close(conn, cur)
    return redirect('/lab5')

@lab5.route('/lab5/list')
def list():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))

    user_id = cur.fetchone()["id"]

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE user_id=%s ORDER BY is_favorite DESC;", (user_id,))
    else:
        cur.execute("SELECT * FROM articles WHERE user_id=? ORDER BY is_favorite DESC;", (user_id,))
        
    articles = cur.fetchall()

    db_close(conn, cur)
    return render_template('/lab5/articles.html', articles=articles)

@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab5/login')

@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    login = session.get('login')

    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
    user_row = cur.fetchone()
    if not user_row:
        db_close(conn, cur)
        return redirect('/lab5/login')
    user_id = user_row['id']

    if request.method == 'POST':
        title = request.form.get('title')
        article_text = request.form.get('article_text')

        is_public = True if request.form.get('is_public') else False
        is_favorite = True if request.form.get('is_favorite') else False

        if not title or not article_text:
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT * FROM articles WHERE id = %s AND user_id = %s;", (article_id, user_id))
            else:
                cur.execute("SELECT * FROM articles WHERE id = ? AND user_id = ?;", (article_id, user_id))
            article = cur.fetchone()
            db_close(conn, cur)
            return render_template('lab5/edit_article.html', article=article, error="Заполните все поля!")

        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "UPDATE articles SET title = %s, article_text = %s, is_public = %s, is_favorite = %s WHERE id = %s AND user_id = %s;",
                (title, article_text, is_public, is_favorite, article_id, user_id)
            )
        else:
            cur.execute(
                "UPDATE articles SET title = ?, article_text = ?, is_public = ?, is_favorite = ? WHERE id = ? AND user_id = ?;",
                (title, article_text, is_public, is_favorite, article_id, user_id)
            )

        db_close(conn, cur)
        return redirect('/lab5/list')

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE id = %s AND user_id = %s;", (article_id, user_id))
    else:
        cur.execute("SELECT * FROM articles WHERE id = ? AND user_id = ?;", (article_id, user_id))
    article = cur.fetchone()
    db_close(conn, cur)

    if not article:
        return "Статья не найдена или у вас нет прав", 404

    return render_template('lab5/edit_article.html', article=article)

@lab5.route('/lab5/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
    user_id = cur.fetchone()['id']

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id = %s AND user_id = %s;", (article_id, user_id))
    else:
        cur.execute("DELETE FROM articles WHERE id = ? AND user_id = ?;", (article_id, user_id))

    db_close(conn, cur)
    return redirect('/lab5/list')

@lab5.route('/lab5/users')
def users_list():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login, real_name FROM users;")
    else:
        cur.execute("SELECT login, real_name FROM users;")
        
    users = cur.fetchall()
    db_close(conn, cur)
    
    return render_template('lab5/users.html', users=users)

@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')

    conn, cur = db_connect()
    error = None
    success = None

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT real_name FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT real_name FROM users WHERE login = ?;", (login,))
    
    current_user = cur.fetchone()
    current_name_before = current_user['real_name']

    if request.method == 'POST':
        real_name = request.form.get('real_name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        name_changed = False
        if real_name != current_name_before:
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE users SET real_name = %s WHERE login = %s;", (real_name, login))
            else:
                cur.execute("UPDATE users SET real_name = ? WHERE login = ?;", (real_name, login))
            name_changed = True

        password_changed = False
        if password:
            if password == password_confirm:
                password_hash = generate_password_hash(password)
                if current_app.config['DB_TYPE'] == 'postgres':
                    cur.execute("UPDATE users SET password = %s WHERE login = %s;", (password_hash, login))
                else:
                    cur.execute("UPDATE users SET password = ? WHERE login = ?;", (password_hash, login))
                password_changed = True
            else:
                error = "Пароли не совпадают"

        if name_changed and password_changed:
            success = "Имя и пароль успешно обновлены"
        elif name_changed:
            success = "Имя успешно обновлено"
        elif password_changed:
            success = "Пароль успешно обновлен"

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT real_name FROM users WHERE login = %s;", (login,))
    else:
        cur.execute("SELECT real_name FROM users WHERE login = ?;", (login,))
    
    current_user_after = cur.fetchone()
    current_name = current_user_after['real_name']
    
    db_close(conn, cur)

    return render_template('lab5/profile.html', current_name=current_name, error=error, success=success)

@lab5.route('/lab5/public')
def public_articles():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM articles WHERE is_public = TRUE ORDER BY likes DESC, id DESC;")
    else:
        cur.execute("SELECT * FROM articles WHERE is_public = 1 ORDER BY likes DESC, id DESC;")
        
    articles = cur.fetchall()
    db_close(conn, cur)
    
    return render_template('lab5/public_articles.html', articles=articles)

@lab5.route('/lab5/like_article/<int:article_id>', methods=['POST'])
def like_article(article_id):
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE articles SET likes = likes + 1 WHERE id = %s;", (article_id,))
    else:
        cur.execute("UPDATE articles SET likes = likes + 1 WHERE id = ?;", (article_id,))
    
    db_close(conn, cur)

    return redirect('/lab5/public')