from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
app = Flask(__name__)

access_log = []

@app.errorhandler(404)
def not_found(err):
    img_path = url_for('static', filename='404.jpg')
    css_path = url_for('static', filename='404.css')

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

                <h2>Список роутов:</h2>
                <ul>
                    <li><a href="/lab1/web">/lab1/web</a></li>
                    <li><a href="/lab1/author">/lab1/author</a></li>
                    <li><a href="/lab1/image">/lab1/image</a></li>
                    <li><a href="/lab1/counter">/lab1/counter</a></li>
                    <li><a href="/lab1/counter/clear">/lab1/counter/clear</a></li>
                    <li><a href="/lab1/info">/lab1/info</a></li>
                    <li><a href="/lab1/created">/lab1/created</a></li>
                    <li><a href="/lab1/error/400">/lab1/error/400</a></li>
                    <li><a href="/lab1/error/401">/lab1/error/401</a></li>
                    <li><a href="/lab1/error/402">/lab1/error/402</a></li>
                    <li><a href="/lab1/error/403">/lab1/error/403</a></li>
                    <li><a href="/lab1/error/405">/lab1/error/405</a></li>
                    <li><a href="/lab1/error/418">/lab1/error/418</a></li>
                    <li><a href="/lab1/trigger500">/lab1/trigger500</a></li>
                </ul>
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

    html = '''<!doctype html>
        <html>
            <head>
                <title>Сакура</title>
                <link rel="stylesheet" href="''' + css_path + '''">
            </head>
            <body>
                <h1>Сакура</h1>
                <img class="sakura" src="''' + path + '''" alt="Сакура">
            </body>
        </html>'''
    
    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Language': 'ru',
        'X-Student-Name': 'Aleksandra Denisenko',
        'X-Lab': 'Lab-1'
    }
    
    return html, 200, headers

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

@app.route('/lab1/error/400')
def error_400():
    return '''<!doctype html>
        <html>
            <body>
                <h1>400 Bad Request</h1>
                <p>Сервер не смог понять запрос из-за неверного синтаксиса.</p>
            </body>
        </html>''', 400, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/lab1/error/401')
def error_401():
    return '''<!doctype html>
        <html>
            <body>
                <h1>401 Unauthorized</h1>
                <p>Требуются учетные данные для доступа к ресурсу.</p>
            </body>
        </html>''', 401, {
            'Content-Type': 'text/html; charset=utf-8',
            'WWW-Authenticate': 'Basic realm="Login Required"'
            }

@app.route('/lab1/error/402')
def error_402():
    return '''<!doctype html>
        <html>
            <body>
                <h1>402 Payment Required</h1>
                <p>Зарезервировано для будущего использования.</p>
            </body>
        </html>''', 402, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/lab1/error/403')
def error_403():
    return '''<!doctype html>
        <html>
            <body>
                <h1>403 Forbidden</h1>
                <p>Клиент не имеет прав доступа к контенту.</p>
            </body>
        </html>''', 403, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/lab1/error/405')
def error_405():
    return '''<!doctype html>
        <html>
            <body>
                <h1>405 Method Not Allowed</h1>
                <p>Используемый HTTP-метод не разрешён для данного ресурса.</p>
            </body>
        </html>''', 405, {
            'Content-Type': 'text/html; charset=utf-8',
            'Allow': 'GET'
            }

@app.route('/lab1/error/418')
def error_418():
    return '''<!doctype html>
        <html>
            <body>
                <h1>418 I'm a teapot</h1>
                <p>«Шуточный» ответ: сервер отклоняет попытку заварить кофе в чайнике.</p>
            </body>
        </html>''', 418, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/lab1/trigger500')
def trigger_500():
    return 1 / 0

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

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ['Роза', 'Тюльпан', 'Пион', 'Ромашка', 'Лилия']

@app.route('/lab2/flowers')
def flowers_all():
    items = ''
    for name in flower_list:
        items += f'<li>{name}</li>'
    if not items:
        items = '<li>Список пуст</li>'
    return f'''<!doctype html>
    <html>
        <body>
            <h1>Список всех цветов</h1>
            <p>Всего цветов: <b>{len(flower_list)}</b></p>
            <ul>
                {items}
            </ul>
            <p><a href="/lab2/flowers/clear">Очистить список цветов</a></p>
        </body>
    </html>'''

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list) or flower_id < 0:
        abort(404)
    name = flower_list[flower_id]
    return f'''<!doctype html>
    <html>
        <body>
            <h1>Информация о цветке</h1>
            <p><b>ID:</b> {flower_id}</p>
            <p><b>Название:</b> {name}</p>
            <p><a href="/lab2/flowers">Посмотреть список всех цветов</a></p>
        </body>
    </html>'''

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''<!doctype html>
    <html>
        <body>
            <h1>Добавлен новый цветок</h1>
            <p><b>Название нового цветка:</b> {name}</p>
            <p><b>Всего цветов:</b> {len(flower_list)}</p>
            <p><b>Полный список цветов:</b> {flower_list}</p>
        </body>
    </html>'''

@app.route('/lab2/add_flower/')
def add_flower_missing():
    return 'Вы не задали имя цветка.', 400

@app.route('/lab2/flowers/clear')
def clear_flowers():
    global flower_list
    flower_list = []
    return '''<!doctype html>
    <html>
        <body>
            <h1>Список цветов очищен</h1>
            <p><a href="/lab2/flowers">Посмотреть весь список цветов</a></p>
        </body>
    </html>'''

@app.route('/lab2/example')
def example():
    name = 'Денисенко Александра Юрьевна'
    group = 'ФБИ-31'
    course = '3 курс'
    number = '2'
    fruits = [
        {'name': 'Яблоки', 'price': 100},
        {'name': 'Груши', 'price': 120},
        {'name': 'Апельсины', 'price': 80},
        {'name': 'Мандарины', 'price': 95},
        {'name': 'Манго', 'price': 321}
    ]
    return render_template('example.html', name=name, group=group, 
                           course=course, number=number, fruits=fruits)

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "0 <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase=phrase)

@app.route('/lab2/calc/')
def calc_default():
    return redirect(url_for('calc_ab', a=1, b=1))

@app.route('/lab2/calc/<int:a>')
def calc_a(a):
    return redirect(url_for('calc_ab', a=a, b=1))

@app.route('/lab2/calc/<int:a>/<int:b>/')
def calc_ab(a, b):
    add = a + b
    sub = a - b
    mul = a * b

    if b == 0:
        div = "На 0 делить нельзя"
    else:
        if a % b == 0:
            div = str(a // b)
        else:
            div = f"{a / b:.2f}"

    power = a ** b

    return render_template(
        'calc.html',
        a=a, b=b,
        add=add, sub=sub, mul=mul, div=div, power=power
    )