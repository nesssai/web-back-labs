// Функция для загрузки и отрисовки списка фильмов
function fillFilmList() {
    // Отправляем GET-запрос к API для получения всех фильмов
    fetch('/lab7/rest-api/films/')
    .then(function (data) {
        return data.json(); // Преобразуем ответ от сервера в JSON
    })
    .then(function (films) {
        // Находим таблицу в DOM и очищаем её текущее содержимое
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        // Проходим циклом по всем полученным фильмам и создаем строки таблицы
        for(let i = 0; i < films.length; i++) {
            let tr = document.createElement('tr');
            
            // Создаем ячейки для данных
            let tdTitleRus = document.createElement('td');
            let tdTitle = document.createElement('td');
            let tdYear = document.createElement('td');
            let tdActions = document.createElement('td');

            // Заполняем русское название
            tdTitleRus.innerText = films[i].title_ru;

            // Заполняем оригинальное название, если оно есть
            if (films[i].title && films[i].title !== '') {
                let span = document.createElement('span');
                span.className = 'original-title';
                span.innerText = '(' + films[i].title + ')';
                tdTitle.appendChild(span);
            } else {
                tdTitle.innerText = '';
            }

            // Заполняем год выпуска
            tdYear.innerText = films[i].year;

            // Создаем кнопку "Редактировать"
            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';
            // При клике вызываем функцию редактирования, передавая реальный ID фильма из БД
            editButton.onclick = function() {
                editFilm(films[i].id); 
            };

            // Создаем кнопку "Удалить"
            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';
            // При клике вызываем функцию удаления, передавая реальный ID и название (для подтверждения)
            delButton.onclick = function() {
                deleteFilm(films[i].id, films[i].title_ru);
            };

            // Добавляем кнопки в ячейку действий
            tdActions.append(editButton);
            tdActions.append(delButton);
            
            // Собираем строку из ячеек
            tr.append(tdTitleRus);
            tr.append(tdTitle);
            tr.append(tdYear);
            tr.append(tdActions);
            
            // Добавляем готовую строку в таблицу
            tbody.append(tr);
        }
    })
}

// Функция для удаления фильма
function deleteFilm(id, title) {
    // Спрашиваем подтверждение у пользователя
    if(! confirm(`Вы точно хотите удалить фильм "${title}"?`))
        return;

    // Отправляем DELETE-запрос на сервер по конкретному ID
    fetch(`/lab7/rest-api/films/${id}`, {method: 'DELETE'})
        .then(function () {
            // После успешного удаления обновляем список на странице
            fillFilmList();
        });
}

// Функции управления модальным окном
function showModal() {
    document.querySelector('div.modal').style.display = 'block';
}

function hideModal() {
    document.querySelector('div.modal').style.display = 'none';
}

function cancel() {
    hideModal();
}

// Подготовка модального окна для добавления нового фильма
function addFilm() {
    // Очищаем скрытое поле ID (пустой ID означает создание новой записи)
    document.getElementById('id').value = '';
    
    // Очищаем поля ввода
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    
    // Сбрасываем тексты ошибок с прошлого раза
    document.getElementById('title-error').innerText = '';
    document.getElementById('title-ru-error').innerText = '';
    document.getElementById('year-error').innerText = '';
    document.getElementById('description-error').innerText = '';

    showModal();
}

// Отправка данных формы на сервер (создание или редактирование)
function sendFilm() {
    const id = document.getElementById('id').value;
    // Собираем данные из полей ввода в объект
    const film = {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title-ru').value,
        year: document.getElementById('year').value,
        description: document.getElementById('description').value
    }

    // Формируем URL. Если ID пустой — создаем новый ресурс (POST), иначе обновляем старый (PUT)
    const url = `/lab7/rest-api/films/${id}`;
    const method = id === '' ? 'POST' : 'PUT';

    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film) // Превращаем объект в JSON-строку
    })
    .then(function(resp) {
        // Если сервер ответил "ОК" (200-299)
        if(resp.ok) {
            fillFilmList(); // Обновляем таблицу
            hideModal();    // Закрываем окно
            return {};
        }
        // Если ошибка — парсим JSON с описанием ошибок
        return resp.json();
    })
    .then(function(errors) {
        // Если пришли ошибки валидации — отображаем их под соответствующими полями
        if (!errors) return;
        if (errors.title) document.getElementById('title-error').innerText = errors.title;
        if (errors.title_ru) document.getElementById('title-ru-error').innerText = errors.title_ru;
        if (errors.year) document.getElementById('year-error').innerText = errors.year;
        if (errors.description) document.getElementById('description-error').innerText = errors.description;
    });
}

// Подготовка модального окна для редактирования существующего фильма
function editFilm(id) {
    // Сначала запрашиваем актуальные данные фильма с сервера по ID
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function (data) {
        return data.json();
    })
    .then(function (film) {
        // Заполняем поля формы полученными данными
        document.getElementById('id').value = id; // Сохраняем ID, чтобы потом знать, что обновлять
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        
        // Очищаем старые ошибки
        document.getElementById('title-error').innerText = '';
        document.getElementById('title-ru-error').innerText = '';
        document.getElementById('year-error').innerText = '';
        document.getElementById('description-error').innerText = '';
        
        showModal();
    });
}
