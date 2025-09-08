from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "Такой страницы не существует :(", 404

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

@app.route('/lab1')
def lab1():
    return """<!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>Лабораторная 1</title>
            </head>
            <body>
                <p>
                Flask &mdash; фреймворк для создания веб-приложений на языке программирования Python,
                использующий набор инструментов Werkzeug, а также шаблонизатор Jinja2.
                Относится к категории так называемых микрофреймворков &mdash; минималистичных каркасов
                веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
                </p>

                <p><a href="/">На главную</a></p>
            </body>
        </html>"""

@app.route("/lab1/web")
def web():
    return """<!doctype html>
        <html>
            <body>
               <h1>web-сервер на flask</h1>
               <a href="/lab1/author">author<a>
            </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
            }

@app.route("/lab1/author")
def author():
    name = "Денисенко Александра Юрьевна"
    group = "ФБИ-31"
    faculty = "ФБ"

    return """<!doctype html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/lab1/web">web<a>
            </body>
        </html>"""

@app.route('/lab1/image')
def image():
    path = url_for("static", filename="sakura.jpg")
    css_path = url_for("static", filename="lab1.css")
    return '''<!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>Сакура</title>
                <link rel="stylesheet" href="''' + css_path + '''">
            </head>
            <body>
                <h1>Сакура</h1>
                <img class="sakura" src="''' + path + '''" alt="Сакура">
            </body>
        </html>'''

count = 0

@app.route('/lab1/counter')
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''<!doctype html>
        <html>
            <body>
                Сколько раз вы сюда заходили: ''' + str(count) + '''
                <hr>
                Дата и время: ''' + str(time) + '''<br>
                Запрошенный адрес: ''' + url + '''<br>
                Ваш IP адрес: ''' + client_ip + '''<br>
                <hr>
                <a href="/lab1/counter/clear">Очистить счётчик</a>
            </body>
        </html>'''

@app.route('/lab1/counter/clear')
def counter_clear():
    global count
    count = 0
    return '''<!doctype html>
        <html>
            <body>
                <h1>Счётчик очищен</h1>
                <p>Значение счётчика теперь равно 0</p>
                <a href="/lab1/counter">Вернуться на страницу счётчика</a>
            </body>
        </html>'''

@app.route('/lab1/info')
def info():
    return redirect("/lab1/author")

@app.route("/lab1/created")
def created():
    return '''<!doctype html>
        <html>
            <body>
                <h1>Создано успешно</h1>
                <div><i>что-то создано...</i></div>
            </body>
        </html>''', 201

@app.route('/error/400')
def error_400():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>400 Bad Request</title></head>
            <body>
                <h1>400 Bad Request</h1>
                <p>Сервер не смог понять запрос из-за неверного синтаксиса.</p>
            </body>
        </html>''', 400, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/error/401')
def error_401():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>401 Unauthorized</title></head>
            <body>
                <h1>401 Unauthorized</h1>
                <p>Требуются учетные данные для доступа к ресурсу.</p>
            </body>
        </html>''', 401, {
            'Content-Type': 'text/html; charset=utf-8',
            'WWW-Authenticate': 'Basic realm="Login Required"'
            }

@app.route('/error/402')
def error_402():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>402 Payment Required</title></head>
            <body>
                <h1>402 Payment Required</h1>
                <p>Зарезервировано для будущего использования.</p>
            </body>
        </html>''', 402, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/error/403')
def error_403():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>403 Forbidden</title></head>
            <body>
                <h1>403 Forbidden</h1>
                <p>Клиент не имеет прав доступа к контенту.</p>
            </body>
        </html>''', 403, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/error/405')
def error_405():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>405 Method Not Allowed</title></head>
            <body>
                <h1>405 Method Not Allowed</h1>
                <p>Используемый HTTP-метод не разрешён для данного ресурса.</p>
            </body>
        </html>''', 405, {
            'Content-Type': 'text/html; charset=utf-8',
            'Allow': 'GET'
            }

@app.route('/error/418')
def error_418():
    return '''<!doctype html>
        <html>
            <head><meta charset="utf-8"><title>418 I'm a teapot</title></head>
            <body>
                <h1>418 I'm a teapot</h1>
                <p>«Шуточный» ответ: сервер отклоняет попытку заварить кофе в чайнике.</p>
            </body>
        </html>''', 418, {'Content-Type': 'text/html; charset=utf-8'}
