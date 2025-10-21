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
            user = next((u for u in users if u['login'] == session['login']), None)
            if user:
                username = user['name']
                gender = user['gender']
                gender_text = 'мужской' if gender == 'М' else 'женский'
                return render_template('lab4/login.html', authorized=authorized, username=username, gender_text=gender_text)
        else:
            return render_template('lab4/login.html', authorized=False)

    login = request.form.get('login')
    password = request.form.get('password')

    if not login:
        return render_template('lab4/login.html', error='Не введён логин', login=login, authorized=False)
    if not password:
        return render_template('lab4/login.html', error='Не введён пароль', login=login, authorized=False)
    
    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            return redirect('/lab4/login')
    
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error='Неверные логин и/или пароль', login=login, authorized=False)

@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')