from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "Такой страницы не существует :(", 404

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
