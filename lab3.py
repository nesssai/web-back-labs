from flask import Blueprint, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)

@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name', 'Дикий огурец')
    name_color = request.cookies.get('name_color', "#136617")
    age = request.cookies.get('age', 'неизвестно')
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)

@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Балерина Капучино', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', "#df2d6e")
    return resp

@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp

@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'
    age = request.args.get('age')
    sex = request.args.get('sex')
    if age == '':
        errors['age'] = 'Заполните поле!'
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)

@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')

@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    
    if drink == 'espresso':
        price = 129
    elif drink == 'americano':
        price = 219
    elif drink == 'latte':
        price = 229
    elif drink == 'cappuccino':
        price = 229
    elif drink == 'raff':
        price = 259
    else:
        price = 189
    
    if request.args.get('milk') == 'on':
        price += 80
    if request.args.get('sugar') == 'on':
        price += 10
    if request.args.get('cinnamon') == 'on':
        price += 10
    if request.args.get('syrup') == 'on':
        price += 30
    
    return render_template('lab3/pay.html', price=price)

@lab3.route('/lab3/success')
def success():
    price = request.args.get('price')
    return render_template('lab3/success.html', price=price)

@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bg_color = request.args.get('bg_color')
    font_size = request.args.get('font_size')
    font_family = request.args.get('font_family')
    
    if color or bg_color or font_size or font_family:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bg_color:
            resp.set_cookie('bg_color', bg_color)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if font_family:
            resp.set_cookie('font_family', font_family)
        return resp
    
    color = request.cookies.get('color')
    bg_color = request.cookies.get('bg_color')
    font_size = request.cookies.get('font_size')
    font_family = request.cookies.get('font_family')
    
    resp = make_response(render_template('lab3/settings.html', 
                                         color=color, 
                                         bg_color=bg_color, 
                                         font_size=font_size, 
                                         font_family=font_family))
    return resp

@lab3.route('/lab3/settings/clear')
def clear_settings():
    resp = make_response(redirect('/lab3/settings'))
    resp.delete_cookie('color')
    resp.delete_cookie('bg_color')
    resp.delete_cookie('font_size')
    resp.delete_cookie('font_family')
    return resp

@lab3.route('/lab3/ticket')
def ticket():
    return render_template('lab3/ticket.html', errors={})

@lab3.route('/lab3/ticket_result')
def ticket_result():
    errors = {}
    
    fio = request.args.get('fio')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    age = request.args.get('age')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')

    if fio == '':
        errors['fio'] = 'Заполните поле ФИО'
    if age == '':
        errors['age'] = 'Заполните возраст'
    else:
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 120:
                errors['age'] = 'Возраст должен быть от 1 до 120 лет'
        except ValueError:
            errors['age'] = 'Возраст должен быть числом'
    if departure == '':
        errors['departure'] = 'Заполните пункт выезда'
    if destination == '':
        errors['destination'] = 'Заполните пункт назначения'
    if date == '':
        errors['date'] = 'Выберите дату поездки'

    if errors:
        return render_template('lab3/ticket.html', 
                             errors=errors, fio=fio, shelf=shelf,
                             linen=linen, baggage=baggage, age=age,
                             departure=departure, destination=destination,
                             date=date, insurance=insurance)

    age_int = int(age)
    
    if age_int >= 18:
        price = 1000
        ticket_type = "Взрослый"
    else:
        price = 700
        ticket_type = "Детский"

    if shelf in ['lower', 'lower_side']:
        price += 100
    if linen == 'on':
        price += 75
    if baggage == 'on':
        price += 250
    if insurance == 'on':
        price += 150

    return render_template('lab3/ticket_result.html',
                         fio=fio, shelf=shelf, linen=linen,
                         baggage=baggage, age=age_int, departure=departure,
                         destination=destination, date=date, insurance=insurance,
                         price=price, ticket_type=ticket_type)