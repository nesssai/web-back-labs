import random
from flask import Blueprint, render_template, request, session, jsonify

# Создаем blueprint для модуля lab9
lab9 = Blueprint('lab9', __name__)

gifts = []  # Список, в котором хранятся все подарки


def init_gifts():
    # Инициализация списка подарков (один раз при запуске)
    if gifts:
        return

    congratulations = [
        "Счастья в новом году!", "Удачи во всем!", "Крепкого здоровья!",
        "Любви и тепла!", "Ярких эмоций!", "Исполнения желаний!",
        "Новых побед!", "Верных друзей!", "Много денег!", "Путешествий!"
    ]

    for i in range(10):
        image_name = f"gift{i+1}.png"
        inner_image_name = f"toy{i+1}.png"

        # Каждый подарок имеет внешний и внутренний вид, поздравление и координаты
        gifts.append({
            "id": i,
            "opened": False,
            "congratulation": congratulations[i],
            "image": f"/static/lab9/{image_name}", 
            "inner_image": f"/static/lab9/{inner_image_name}", 
            "top": random.randint(10, 500),    # Случайное положение по вертикали
            "left": random.randint(10, 1100)   # Случайное положение по горизонтали
        })


init_gifts()  # Инициализируем подарки при загрузке модуля


@lab9.route('/lab9/', methods=['GET'])
def main():
    # Отображение главной страницы с подарками
    if 'gift_counter' not in session:
        session['gift_counter'] = 0

    # Подсчет количества неоткрытых подарков
    closed_count = sum(1 for g in gifts if not g['opened'])
    return render_template('lab9/index.html', gifts=gifts, count=closed_count)


@lab9.route('/lab9/rest-api/gifts/<int:id>', methods=['POST'])
def open_gift(id):
    # Проверяем, что пользователь не открыл более 3 подарков
    if session.get('gift_counter', 0) >= 3:
        return jsonify({"error": "Вы уже открыли 3 подарка! Хватит жадничать :)"}), 400

    # Ищем подарок по ID из URL
    gift = next((g for g in gifts if g['id'] == id), None)
    
    if not gift:
        return jsonify({"error": "Подарок не найден"}), 404
        
    if gift['opened']:
        return jsonify({"error": "Этот подарок уже пуст!"}), 409
    
    # Помечаем подарок как открытый и увеличиваем счетчик пользователя
    gift['opened'] = True
    session['gift_counter'] += 1
    
    # Возвращаем данные открытого подарка (внутреннее изображение и поздравление)
    return jsonify({
        "result": "success",
        "image": gift['inner_image'], 
        "congratulation": gift['congratulation']
    })


# Сброс всех подарков и счетчиков
@lab9.route('/lab9/rest-api/gifts/reset', methods=['POST'])
def reset_all():
    session['gift_counter'] = 0
    for g in gifts:
        g['opened'] = False
    return jsonify({"success": True})