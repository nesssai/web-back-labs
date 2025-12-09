from flask import Blueprint, render_template, request, abort
from datetime import datetime

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

films = [
    {
        "title": "Shutter Island",
        "title_ru": "Остров проклятых",
        "year": 2009,
        "description": "Психологический триллер Мартина Скорсезе о двух федеральных маршалах, прибывающих в психиатрическую лечебницу на изолированном острове для расследования исчезновения пациентки. Детектив Тедди Дэниелс сталкивается с паутиной загадок, где грань между реальностью и безумием постепенно стирается."
    },
    {
        "title": "Avengers: Endgame",
        "title_ru": "Мстители: Финал",
        "year": 2019,
        "description": "Эпический финал Саги Бесконечности Marvel, где Мстители объединяются для последней битвы с Таносом, чтобы вернуть половину жизни во вселенной."
    },
    {
        "title": "Titanic",
        "title_ru": "Титаник",
        "year": 1997,
        "description": "Романтическая драма Джеймса Кэмерона о трагической любви Джека и Роуз на борту легендарного лайнера Титаник во время его первого и последнего плавания."
    },
    {
        "title": "Interstellar",
        "title_ru": "Интерстеллар",
        "year": 2014,
        "description": "Эпический научно-фантастический фильм Кристофера Нолана о группе исследователей, которые отправляются сквозь червоточину в путешествие, чтобы найти планету с подходящими для человечества условиями и спасти цивилизацию от вымирания."
    },
    {
        "title": "Twilight",
        "title_ru": "Сумерки",
        "year": 2008,
        "description": "Романтическое фэнтези о 17-летней Белле Суон, которая переезжает в городок Форкс и влюбляется в загадочного Эдварда Каллена — вампира из семьи, питающейся кровью животных."
    },
]

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

    # Год: приводим к int и проверяем диапазон
    try:
        year = int(year_raw)
        current_year = datetime.now().year
        if year < 1895 or year > current_year:
            errors['year'] = f'Год должен быть от 1895 до {current_year}'
        else:
            film['year'] = year
    except (TypeError, ValueError):
        errors['year'] = 'Некорректный год'

    return errors

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    return films[id]

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    del films[id]
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        abort(404)

    film = request.get_json()
    errors = validate_film(film)
    if errors:
        return errors, 400

    films[id] = film
    return films[id]

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()

    errors = validate_film(film)
    if errors:
        return errors, 400

    films.append(film)
    return {"id": len(films) - 1}, 201
