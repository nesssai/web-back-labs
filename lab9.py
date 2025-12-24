import random
from flask import Blueprint, render_template, request, session, jsonify
from flask_login import current_user

lab9 = Blueprint('lab9', __name__)

gifts = []

def init_gifts():
    if gifts:
        return
    
    congratulations = [
        "Счастья в новом году!", "Удачи во всем!", "Крепкого здоровья!",
        "Любви и тепла!", "Ярких эмоций!", "Исполнения желаний!",
        "Новых побед!", "Верных друзей!", "Много денег!", "Путешествий!"
    ]
    
    # Подарки 5, 6, 7 требуют авторизации
    auth_required_ids = [5, 6, 7]
    
    for i in range(10):
        image_name = f"gift{i+1}.png"
        inner_image_name = f"toy{i+1}.png"
        gifts.append({
            "id": i,
            "opened": False,
            "congratulation": congratulations[i],
            "image": f"/static/lab9/{image_name}",
            "inner_image": f"/static/lab9/{inner_image_name}",
            "top": random.randint(10, 500),
            "left": random.randint(10, 1100),
            "auth_required": i in auth_required_ids
        })

init_gifts()

@lab9.route('/lab9/', methods=['GET'])
def main():
    if 'gift_counter' not in session:
        session['gift_counter'] = 0
    
    closed_count = sum(1 for g in gifts if not g['opened'])
    is_authenticated = current_user.is_authenticated
    
    return render_template('lab9/index.html', 
                         gifts=gifts, 
                         count=closed_count,
                         is_authenticated=is_authenticated)

@lab9.route('/lab9/rest-api/gifts/<int:id>', methods=['POST'])
def open_gift(id):
    gift = next((g for g in gifts if g['id'] == id), None)
    
    if not gift:
        return jsonify({"error": "Подарок не найден"}), 404
    
    if gift['opened']:
        return jsonify({"error": "Этот подарок уже пуст!"}), 409
    
    # Проверка авторизации для особых подарков
    if gift['auth_required'] and not current_user.is_authenticated:
        return jsonify({"error": "Этот подарок доступен только авторизованным пользователям!"}), 403
    
    if session.get('gift_counter', 0) >= 3:
        return jsonify({"error": "Вы уже открыли 3 подарка! Хватит жадничать :)"}), 400
    
    gift['opened'] = True
    session['gift_counter'] += 1
    
    return jsonify({
        "result": "success",
        "image": gift['inner_image'],
        "congratulation": gift['congratulation']
    })

@lab9.route('/lab9/rest-api/gifts/reset', methods=['POST'])
def reset_all():
    session['gift_counter'] = 0
    for g in gifts:
        g['opened'] = False
    return jsonify({"success": True})