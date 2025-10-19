from flask import Flask, url_for, request
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4

import datetime
app = Flask(__name__)

app.secret_key = 'секретно-секретный секрет'

app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)

access_log = []

@app.errorhandler(404)
def not_found(err):
    img_path = url_for('static', filename='lab1/404.jpg')
    css_path = url_for('static', filename='lab1/404.css')

    # Определяем IP-адрес
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        ip = xff.split(',')[0].strip()
    else:
        ip = request.remote_addr or 'Unknown'

    # "Достаём" дату доступа
    access_time = datetime.datetime.now().strftime('%d.%m.%Y в %H:%M:%S')

    # Запрошенный адрес
    requested_url = request.url

    # Добавляем запись в in-memory лог
    access_log.append({
        'ip': ip,
        'time': access_time,
        'url': requested_url
    })

    # Формируем HTML-список лога
    log_items = ''
    for entry in access_log:
        log_items += '<li> Пользователь {ip} {time} зашёл на адрес: {url}</li>'.format(**entry)

    return '''<!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>404 — Не найдено</title>
                <link rel="stylesheet" href="''' + css_path + '''">
            </head>
            <body>
                <img src="''' + img_path + '''" alt="404">
                <h1>Ой! Такой страницы нет</h1>
                <p>Проверьте адрес или вернитесь на главную</p>

                <div class="info">
                    <h2>Информация о запросе:</h2>
                    <p><b>Ваш IP:</b> ''' + ip + '''</p>
                    <p><b>Дата доступа:</b> ''' + access_time + '''</p>
                </div>
                    <a href="/">Вернуться на главную</a>

                <hr>
                <h2>Журнал обращений:</h2>
                <ul class="log">
                    ''' + log_items + '''
                </ul>
            </body>
        </html>''', 404

@app.route('/')
@app.route('/index')
def index():
    name = "Денисенко Александра Юрьевна"
    group = "ФБИ-31"
    course = "3 курс"
    year = "2025 г."

    return """<!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>НГТУ, ФБ, Лабораторные работы</title>
            </head>
            <body>
                <header>
                    <h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1>
                </header>

                <div>
                    <ul>
                        <li><a href="/lab1">Первая лабораторная</a></li>
                        <li><a href="/lab2/">Вторая лабораторная</a></li>
                        <li><a href="/lab3/">Третья лабораторная</a></li>
                        <li><a href="/lab4/">Четвёртая лабораторная</a></li>
                    </ul>
                </div>

                <footer>
                    <hr>
                    <div style="text-align:right; white-space:nowrap; overflow:hidden;">
                        """ + name + """, """ + group + """, """ + course + """, """ + year + """
                    </div>
                </footer>
            </body>
        </html>"""

@app.errorhandler(500)
def server_error(err):
    return '''<!doctype html>
    <html>
        <body>
            <h1>500 &mdash; Внутренняя ошибка сервера</h1>
            <p>На сервере произошла ошибка. Пожалуйста, попробуйте позже.</p>
            <p><a href="/">Вернуться на главную</a></p>
        </body>
    </html>''', 500