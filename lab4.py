from flask import Blueprint, render_template, request, redirect, session
lab4 = Blueprint('lab4', __name__)

@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')

@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')

@lab4.route('/lab4/div', methods=['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены!')
    
    x1 = int(x1)
    x2 = int(x2)
    if x2 == 0:
        return render_template('lab4/div.html', error='На ноль делить нельзя!')

    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)

@lab4.route('/lab4/add-form')
def add_form():
    return render_template('lab4/add-form.html')

@lab4.route('/lab4/add', methods=['POST'])
def add():
    x1 = request.form.get('x1', '')
    x2 = request.form.get('x2', '')
    
    a = float(x1) if x1.strip() != '' else 0.0
    b = float(x2) if x2.strip() != '' else 0.0
    result = a + b
    return render_template('lab4/add.html', x1=a, x2=b, result=result)

@lab4.route('/lab4/mul-form')
def mul_form():
    return render_template('lab4/mul-form.html')

@lab4.route('/lab4/mul', methods=['POST'])
def mul():
    x1 = request.form.get('x1', '')
    x2 = request.form.get('x2', '')
    
    a = float(x1) if x1.strip() != '' else 1.0
    b = float(x2) if x2.strip() != '' else 1.0
    result = a * b
    return render_template('lab4/mul.html', x1=a, x2=b, result=result)

@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('lab4/sub-form.html')

@lab4.route('/lab4/sub', methods=['POST'])
def sub():
    x1 = request.form.get('x1', '')
    x2 = request.form.get('x2', '')
    if x1.strip() == '' or x2.strip() == '':
        return render_template('lab4/sub.html', error='Оба поля должны быть заполнены')
    
    a = float(x1)
    b = float(x2)
    result = a - b
    return render_template('lab4/sub.html', x1=a, x2=b, result=result)

@lab4.route('/lab4/pow-form')
def pow_form():
    return render_template('lab4/pow-form.html')

@lab4.route('/lab4/pow', methods=['POST'])
def power():
    x1 = request.form.get('x1', '')
    x2 = request.form.get('x2', '')
    if x1.strip() == '' or x2.strip() == '':
        return render_template('lab4/pow.html', error='Оба поля должны быть заполнены')
    
    a = float(x1)
    b = float(x2)
    if a == 0.0 and b == 0.0:
        return render_template('lab4/pow.html', error='0^0 не определено')
    
    result = a ** b
    return render_template('lab4/pow.html', x1=a, x2=b, result=result)

tree_count = 0

@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count)
    
    operation = request.form.get('operation')

    if operation == 'cut':
        if tree_count > 0:
                tree_count -= 1
    elif operation == 'plant':
        if tree_count < 15:
                tree_count += 1
        
    return redirect ('/lab4/tree')

users = [
    {'login': 'alex', 'password': '123', 'name': 'Александр', 'gender': 'М'},
    {'login': 'bob', 'password': '555', 'name': 'Борис', 'gender': 'М'},
    {'login': 'pin', 'password': '936', 'name': 'Пин', 'gender': 'М'},
    {'login': 'yezhik', 'password': '149', 'name': 'Ежик', 'gender': 'М'},
    {'login': 'krosh', 'password': '299', 'name': 'Крош', 'gender': 'М'},
    {'login': 'nyusha', 'password': '131', 'name': 'Нюша', 'gender': 'Ж'}
]

@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            user_login = session['login']
            user = next((u for u in users if u['login'] == user_login), None)
            
            if user:
                username = user['name']
                gender = user['gender']
                gender_text = 'мужской' if gender == 'М' else 'женский'
                return render_template('lab4/login.html', authorized=authorized, username=username, gender_text=gender_text)
            else:
                session.pop('login', None)
                return render_template('lab4/login.html', authorized=False)
        else:
            return render_template('lab4/login.html', authorized=False)

    login_form = request.form.get('login')
    password = request.form.get('password')

    if not login_form:
        error = 'Не введён логин'
        return render_template('lab4/login.html', error=error, login=login_form, authorized=False)
    if not password:
        error = 'Не введён пароль'
        return render_template('lab4/login.html', error=error, login=login_form, authorized=False)
    
    for user in users:
        if login_form == user['login'] and password == user['password']:
            session['login'] = login_form 
            return redirect('/lab4/login') 
    
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error=error, login=login_form, authorized=False)

@lab4.route('/lab4/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form.get('login')
        name = request.form.get('name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        gender = request.form.get('gender')

        if not login or not name or not password or not password_confirm or not gender:
            error = 'Все поля обязательны для заполнения'
            return render_template('lab4/register.html', error=error, login=login, name=name, gender=gender)

        if password != password_confirm:
            error = 'Пароли не совпадают'
            return render_template('lab4/register.html', error=error, login=login, name=name, gender=gender)

        if next((u for u in users if u['login'] == login), None):
            error = 'Пользователь с таким логином уже существует'
            return render_template('lab4/register.html', error=error, login=login, name=name, gender=gender)
        
        users.append({'login': login, 'password': password, 'name': name, 'gender': gender})
        
        return redirect('/lab4/login')

    return render_template('lab4/register.html')

@lab4.route('/lab4/users')
def users_list():
    if 'login' not in session:
        return redirect('/lab4/login')
    
    display_users = [{'login': u['login'], 'name': u['name']} for u in users]
    
    return render_template('lab4/users.html', users=display_users, current_user=session['login'])

@lab4.route('/lab4/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    user_login = session['login']
    user = next((u for u in users if u['login'] == user_login), None)

    if user is None:
        session.pop('login', None)
        return redirect('/lab4/login')

    if request.method == 'POST':
        name = request.form.get('name')
        login_new = request.form.get('login')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        gender = request.form.get('gender')

        if not name or not login_new or not gender:
            error = 'Логин, Имя и Пол не могут быть пустыми'
            return render_template('lab4/edit_user.html', error=error, user=user)
        
        if login_new != user_login and next((u for u in users if u['login'] == login_new), None):
            error = 'Этот логин уже занят'
            return render_template('lab4/edit_user.html', error=error, user=user)
        
        user['name'] = name
        user['login'] = login_new
        user['gender'] = gender
        
        if password:
            if password == password_confirm:
                user['password'] = password
            else:
                error = 'Пароли не совпадают, пароль не был изменен'
                return render_template('lab4/edit_user.html', error=error, user=user)
        
        session['login'] = login_new
        
        return redirect('/lab4/users')
    
    return render_template('lab4/edit_user.html', user=user)

@lab4.route('/lab4/delete_user', methods=['POST'])
def delete_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    user_login = session['login']
    user = next((u for u in users if u['login'] == user_login), None)
    
    if user:
        users.remove(user)
    
    session.pop('login', None)
    
    return redirect('/lab4/login')

@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')

@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    error = None
    message = None
    snowflakes = 0
    temp_str = ''

    if request.method == 'POST':
        temp_str = request.form.get('temperature')

        if not temp_str:
            error = "Ошибка: не задана температура"
        else:
            temp = int(temp_str) 

            if temp < -12:
                error = "Не удалось установить температуру - слишком низкое значение"
            elif temp > -1:
                error = "Не удалось установить температуру - слишком высокое значение"
            elif -12 <= temp <= -9:
                message = f"Установлена температура: {temp}°С"
                snowflakes = 3
            elif -8 <= temp <= -5:
                message = f"Установлена температура: {temp}°С"
                snowflakes = 2
            elif -4 <= temp <= -1:
                message = f"Установлена температура: {temp}°С"
                snowflakes = 1

    return render_template('lab4/fridge.html', error=error, message=message, snowflakes=snowflakes, temp=temp_str)

@lab4.route('/lab4/grain', methods=['GET', 'POST'])
def grain_order():
    prices = {
        'barley': 12000,
        'oats': 8500,
        'wheat': 9000,
        'rye': 15000
    }

    grain_names = {
        'barley': 'ячмень',
        'oats': 'овёс',
        'wheat': 'пшеницу',
        'rye': 'рожь'
    }
    
    error = None
    message = None
    selected_grain = ''
    weight_value = ''

    if request.method == 'POST':
        selected_grain = request.form.get('grain_type')
        weight_value = request.form.get('weight')
        
        if not weight_value:
            error = "Ошибка: вес не был указан"
        else:
            weight = float(weight_value)
                
            if weight <= 0:
                error = "Ошибка: указанный вес меньше или равен 0"
                
            elif weight > 100:
                error = "Такого объёма сейчас нет в наличии"
                
            else:
                price_per_ton = prices.get(selected_grain, 0)
                total_cost = weight * price_per_ton
                discount_message = ""
                    
                if weight > 10:
                    discount_amount = total_cost * 0.10
                    total_cost -= discount_amount
                    discount_message = (
                        f"Применена скидка 10% за большой объём. "
                        f"Размер скидки: {discount_amount:.2f} руб."
                    )

                display_name = grain_names.get(selected_grain, 'зерно')
                    
                message = (
                    f"Заказ успешно сформирован. Вы заказали {display_name}. "
                    f"Вес: {weight} т. Сумма к оплате: {total_cost:.2f} руб. "
                    f"{discount_message}"
                )

    return render_template('lab4/grain_order.html', error=error, message=message, selected_grain=selected_grain, weight_value=weight_value)