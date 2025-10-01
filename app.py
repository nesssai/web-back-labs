from flask import Flask, url_for, request, redirect, abort, render_template
from lab1 import lab1

import datetime
app = Flask(__name__)
app.register_blueprint(lab1)

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
                        <li><a href="/lab2/">Вторая лабораторная</a></li>
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

# ЛАБОРАТОРНАЯ РАБОТА 2

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = [
    {"name": "Роза", "price": 150},
    {"name": "Тюльпан", "price": 120},
    {"name": "Пион", "price": 200},
    {"name": "Ромашка", "price": 60},
    {"name": "Лилия", "price": 180}
]

@app.route('/lab2/flowers')
def flowers_all():
    return render_template('flowers.html', flowers=flower_list)

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id < 0 or flower_id >= len(flower_list):
        abort(404)
    flower = flower_list[flower_id]
    return render_template('flower.html', flower=flower, id=flower_id)

@app.route('/lab2/add_flower/<name>/<int:price>')
def add_flower_with_price(name, price):
    flower_list.append({"name": name, "price": price})
    return render_template('flower_added.html', name=name, price=price, flowers=flower_list)

@app.route('/lab2/add_flower/', methods=['GET', 'POST'])
def add_flower():
    name = request.form.get('name', '').strip()
    price = request.form.get('price', '').strip()
    if not name or not price:
        return render_template('add_flower_missing.html'), 400

    flower_list.append({"name": name, "price": price})
    return redirect(url_for('flowers_all'))

@app.route('/lab2/flowers/clear')
def clear_flowers():
    global flower_list
    flower_list = []
    return render_template('flowers_cleared.html')

@app.route('/lab2/flowers/delete/<int:flower_id>')
def delete_flower(flower_id):
    if flower_id < 0 or flower_id >= len(flower_list):
        abort(404)
    flower_list.pop(flower_id)
    return redirect(url_for('flowers_all'))

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

@app.route('/lab2/books/')
def show_books():
    books = [
        {"author": "Ф. М. Достоевский", "title": "Преступление и наказание", "genre": "Роман", "pages": 608},
        {"author": "Л. Н. Толстой", "title": "Война и мир", "genre": "Роман-эпопея", "pages": 1424},
        {"author": "А. С. Пушкин", "title": "Евгений Онегин", "genre": "Роман в стихах", "pages": 224},
        {"author": "А. П. Чехов", "title": "Палата №6", "genre": "Повесть", "pages": 416},
        {"author": "Н. В. Гоголь", "title": "Мёртвые души", "genre": "Поэма", "pages": 320},
        {"author": "И. С. Тургенев", "title": "Отцы и дети", "genre": "Роман", "pages": 286},
        {"author": "М. А. Булгаков", "title": "Мастер и Маргарита", "genre": "Роман", "pages": 517},
        {"author": "А. Н. Толстой", "title": "Пётр Первый", "genre": "Исторический роман", "pages": 768},
        {"author": "В. В. Набоков", "title": "Лолита", "genre": "Роман", "pages": 544},
        {"author": "Б. Л. Пастернак", "title": "Доктор Живаго", "genre": "Роман", "pages": 370},
        {"author": "Кир Булычёв", "title": "Сто лет тому вперёд", "genre": "Научная фантастика", "pages": 352}
    ]
    return render_template('books.html', books=books)

@app.route('/lab2/objects/')
def show_objects():
    cats = [
        {"name": "Барсик", "image": "cat01.jpg", "desc": "Уставший котик, который просто хочет немного поспать, а не делать дедлайны."},
        {"name": "Масик", "image": "cat02.jpg", "desc": "Тусовщик, у него всегда всё помаленьку."},
        {"name": "Бумыч", "image": "cat03.jpg", "desc": "Кот пофигист. Он достиг максимального понимания этого мира."},
        {"name": "Крепыш", "image": "cat04.jpg", "desc": "Качается, чтобы всегда держать себя в форме."},
        {"name": "Автобус", "image": "cat05.jpg", "desc": "Если посмотреть на самого котика, становится ясно, почему такая кличка."},
    ]

    hamsters = [
        {"name": "Лютик", "image": "homa01.jpg", "desc": "Романтичный, с цветочком."},
        {"name": "Мучачос", "image": "homa02.jpg", "desc": "Повар. Очень крутой повар."},
        {"name": "Луна", "image": "homa03.jpg", "desc": "Ночная охотница за товарами на WB."},
        {"name": "Саша", "image": "homa04.jpg", "desc": "Это автор страницы работает на работе."},
        {"name": "Боря", "image": "homa05.jpg", "desc": "Очень трудолюбивый офисный хомяк."},
    ]

    monkeys = [
        {"name": "Кузя", "image": "monkey01.jpg", "desc": "Школьник Кузя (двоечник)."},
        {"name": "Димон", "image": "monkey02.jpg", "desc": "Любит путешествовать и селфи."},
        {"name": "Нюра", "image": "monkey03.jpg", "desc": "Нашла себе хорошего обезьяна и теперь живёт как в шоколаде."},
        {"name": "Бублик", "image": "monkey04.jpg", "desc": "Постоянно о чём-то думает."},
        {"name": "Фунтик", "image": "monkey05.jpg", "desc": "Упитанный парень, улыбчивый."},
    ]

    dogs = [
        {"name": "Рикки", "image": "dog01.jpg", "desc": "Кокетливый. Заигрывает ради вкусняшки."},
        {"name": "Сэм", "image": "dog02.jpg", "desc": "Немного гот. Загадочный."},
        {"name": "Барри", "image": "dog03.jpg", "desc": "Он всегда тебя в чём-то подозревает."},
        {"name": "Кики", "image": "dog04.jpg", "desc": "Кажется злой, но на самом деле милашка (хоть и чихуахуа)."},
        {"name": "Жужа", "image": "dog05.jpg", "desc": "Похожа на домовёнка (возможно им и является)."}
    ]
    return render_template('objects.html', cats=cats, hamsters=hamsters, monkeys=monkeys, dogs=dogs)