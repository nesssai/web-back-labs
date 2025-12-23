from flask import Blueprint, render_template, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import or_

lab8 = Blueprint('lab8', __name__)

@lab8.route('/lab8/')
def lab():
    return render_template('lab8/lab8.html')

# Обработчик регистрации нового пользователя
# GET: отображает форму регистрации
# POST: валидирует логин/пароль, проверяет уникальность логина, создает пользователя с хешированным паролем,
# сохраняет в БД и автоматически авторизует
@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form:
        return render_template('lab8/register.html', error='Логин не может быть пустым')
    
    if not password_form:
        return render_template('lab8/register.html', error='Пароль не может быть пустым')

    login_exists = users.query.filter_by(login = login_form).first()
    if login_exists:
        return render_template('lab8/register.html', 
                            error = 'Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user, remember=False)
    return redirect('/lab8/')

# Обработчик авторизации пользователя
# GET: отображает форму входа
# POST: проверяет логин/пароль, использует хеширование для безопасной проверки,
# авторизует пользователя с опцией "запомнить меня"
@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember_me = request.form.get('remember') == 'on'

    if not login_form:
        return render_template('/lab8/login.html', error='Логин не может быть пустым')
    
    if not password_form:
        return render_template('/lab8/login.html', error='Пароль не может быть пустым')

    user = users.query.filter_by(login = login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember_me)
            return redirect('/lab8/')

    return render_template('/lab8/login.html',
                       error='Ошибка входа: логин и/или пароль неверны')

# Главная страница со списком статей (доступна всем пользователям)
@lab8.route('/lab8/articles/')
# @login_required
def article_list():
    search_query = request.args.get('search', '').strip()

    if current_user.is_authenticated:
        if search_query:
            user_articles = articles.query.filter(
                or_(
                    articles.login_id == current_user.id,
                    articles.is_public == True
                ),
                or_(
                    articles.title.ilike(f'%{search_query}%'),
                    articles.article_text.ilike(f'%{search_query}%')
                )
            ).all()
        else:
            user_articles = articles.query.filter(
                or_(
                    articles.login_id == current_user.id,
                    articles.is_public == True
                )
            ).all()
    else:
        if search_query:
            user_articles = articles.query.filter(
                articles.is_public == True,
                or_(
                    articles.title.ilike(f'%{search_query}%'),
                    articles.article_text.ilike(f'%{search_query}%')
                )
            ).all()
        else:
            user_articles = articles.query.filter_by(is_public=True).all()
    
    return render_template('lab8/articles.html', articles=user_articles, search_query=search_query)

# Создание новой статьи (только для авторизованных пользователей)
@lab8.route('/lab8/create/', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    
    if not title:
        return render_template('lab8/create.html', error='Название не может быть пустым')
    
    if not article_text:
        return render_template('lab8/create.html', error='Текст статьи не может быть пустым')
    
    new_article = articles(
        login_id=current_user.id,
        title=title,
        article_text=article_text,
        is_public=is_public,
        is_favorite=False,
        likes=0
    )
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles/')

# Редактирование существующей статьи (только автор статьи)
@lab8.route('/lab8/edit/<int:article_id>/', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if not article:
        return redirect('/lab8/articles/')
    
    if request.method == 'GET':
        return render_template('lab8/edit.html', article=article)
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_public = request.form.get('is_public') == 'on'
    
    if not title:
        return render_template('lab8/edit.html', article=article, error='Название не может быть пустым')
    
    if not article_text:
        return render_template('lab8/edit.html', article=article, error='Текст статьи не может быть пустым')
    
    article.title = title
    article.article_text = article_text
    article.is_public = is_public
    db.session.commit()
    
    return redirect('/lab8/articles/')

# Удаление статьи (только автор статьи)
@lab8.route('/lab8/delete/<int:article_id>/')
@login_required
def delete_article(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if article:
        db.session.delete(article)
        db.session.commit()
    
    return redirect('/lab8/articles/')

# Выход из системы - завершает сессию пользователя и перенаправляет на главную страницу
@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')