from flask import Flask, request, jsonify, redirect, url_for, Response
import requests
import time
from datetime import datetime
from cryptography.fernet import Fernet
import json
from settings import (
    CLIENT_ID, 
    CLIENT_SECRET, 
    REDIRECT_URI, 
    PG_CONNECTION_STRING
)
from models import db, Request, Parameter, Group, ReceivedGroup 

OATH_URL = 'https://oauth.vk.com/'
ACCESS_TOKEN = ''
key = Fernet.generate_key()
cipher = Fernet(key)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = PG_CONNECTION_STRING 
db.init_app(app)

# Создадим таблицы, если не созданы
with app.app_context():
    db.create_all()


@app.route('/authorization')
def authorization():
    authorization_url = (
        f"{OATH_URL}/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code"
    )
    state = request.args.get('state')
    if state:
        authorization_url += f"&state={state}"
    return (
        "<p>Для отправки запросов Вам необходимо "
        f"<a href='{authorization_url}'>авторизоваться через VK</a></p>"
    )


@app.route('/callback')
def callback():
    global ACCESS_TOKEN
    code = request.args.get('code')
    if code:
        # token_url = f'https://oauth.vk.com/access_token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&redirect_uri={REDIRECT_URI}&code={code}'
        token_url = (
            f"{OATH_URL}access_token?client_id={CLIENT_ID}"
            f"&client_secret={CLIENT_SECRET}"
            f"&redirect_uri={REDIRECT_URI}&code={code}"
        )
        token_response = requests.get(token_url)
        if token_response.status_code == 200:
            response_json = token_response.json()
            ACCESS_TOKEN = response_json.get('access_token', '')

        if ACCESS_TOKEN:
            result = (
                "<p>Авторизация прошла успешно. "
                "Теперь можете отправлять запросы.</p>"
            )
            state = request.args.get('state')
            if state:
                request_url = cipher.decrypt(request.args.get('state')).decode()
                result += f"<a href='{request_url}'>Отправить предыдущий</a>"
            return result
        else:
            return 'Убедитесь, что вы авторизованы в vk.com в браузере.'
        

@app.route('/search_user_and_friends_groups', methods=['GET'])
def search_user_and_friends_groups():
    query = request.args.get('query')
    try:
        user_id_raw = request.args.get('user_id')
        if user_id_raw:
            user_id = int(user_id_raw)
        else:
            return jsonify({'error': 'Missing user_id parameter.'}), 400 
        page = int(request.args.get('page', 0))
        per_page = int(request.args.get('per_page', 0))
    except ValueError:
        # Если в качестве параметров user_id, page, per_page
        # заданы не числовые значение, то возвращаем ошибку
        return jsonify({'error': 'Incorrect parametrs.'}), 400
    if not ACCESS_TOKEN:
        state = cipher.encrypt(request.url.encode())
        return redirect(url_for('authorization', state=state))
    groups = get_user_groups(user_id)
    groups += get_friends_groups(user_id)
    # Убираем повторяющиеся группы
    tuple_list = [tuple(group.items()) for group in groups]
    unique_tuples = set(tuple_list)
    unique_groups = [dict(t) for t in unique_tuples]
    if query:
        # Ищем группы
        matched_groups = search_groups(unique_groups, query)
    else:
        matched_groups = unique_groups
    total_results = len(matched_groups)
    # Если хотя бы один из параметров не задан,
    # то возвращаем все группы
    if page <= 0 or per_page <= 0:
        data = {
            'groups': matched_groups,
            'total_results': total_results,
        }
    else:
        # Получаем нужную часть данных
        paginated_groups = paginate_result(matched_groups, page, per_page)
        data = {
                'groups': paginated_groups,
                'total_results': total_results,
                'page': page,
                'per_page': per_page       
            }
    return construct_response(data)


@app.route('/search_and_write_user_groups', methods=['GET'])
def search_and_write_user_groups():
    parametrs = {}
    query = request.args.get('query')
    parametrs['query'] = query
    try:
        user_id_raw = request.args.get('user_id')
        if user_id_raw:
            parametrs['user_id'] = user_id_raw
            user_id = int(user_id_raw)
        else:
            return jsonify({'error': 'Missing user_id parameter.'}), 400    
        page_raw = request.args.get('page')
        if page_raw:
            parametrs['page'] = page_raw
        else:
            page_raw = 0
        page = int(page_raw)
        per_page_raw = request.args.get('per_page')
        if per_page_raw:
            parametrs['per_page'] = per_page_raw
        else:
            per_page_raw = 0
        per_page = int(per_page_raw)
    except ValueError:
        # Если в качестве параметров user_id, page, per_page
        # заданы не числовые значение, то возвращаем ошибку
        return jsonify({'error': 'Incorrect parametrs.'}), 400
    if not ACCESS_TOKEN:
        state = cipher.encrypt(request.url.encode())
        return redirect(url_for('authorization', state=state))
    groups = get_user_groups(user_id)
    if query:
        # Ищем группы
        matched_groups = search_groups(groups, query)
    else:
        matched_groups = groups
    total_results = len(matched_groups)
    # Если хотя бы один из параметров не задан,
    # то возвращаем все группы
    if page <= 0 or per_page <= 0:
        data = {
            'groups': matched_groups,
            'total_results': total_results,
        }
    else:
        # Получаем нужную часть данных
        paginated_groups = paginate_result(matched_groups, page, per_page)
        data = {
                'groups': paginated_groups,
                'total_results': total_results,
                'page': page,
                'per_page': per_page       
            }
    add_to_db(data, parametrs)
    return construct_response(data)


@app.route('/get_groups_from_db')
def get_groups_from_db():
    try:
        page = int(request.args.get('page', 0))
        per_page = int(request.args.get('per_page', 0))
    except ValueError:
        # Если в качестве параметров page, per_page
        # заданы не числовые значение, то возвращаем ошибку
        return jsonify({'error': 'Incorrect parametrs.'}), 400
    # Создаем базовый объект запроса
    query = db.session.query(Request.created, ReceivedGroup.group_id, Group.name)
    # Применяем операции объединения таблиц
    query = query.outerjoin(ReceivedGroup, Request.id == ReceivedGroup.request_id)
    query = query.outerjoin(Group, Group.id == ReceivedGroup.group_id)
    # Указываем порядок сортировки по полю created в возрастающем порядке
    query = query.order_by(Request.created)
    # Исполняем запрос и получаем результат
    result = query.all()
    data = {}
    data['total_results'] = len(result)
    if page > 0 and per_page > 0:
        result = paginate_result(result, page, per_page)
        data['page'] = page
        data['per_page'] = per_page
    groups = []
    for item in result:
        group = dict(
            created=item[0].isoformat(),
            group=item[1],
            name=item[2]
        )
        groups.append(group)
    data['groups'] = groups
    return construct_response(data) 


def add_to_db(data: dict, parameters: list) -> None:
    new_request = Request(created = datetime.now())
    db.session.add(new_request)
    for param_name in parameters:
        new_parameter = Parameter(
            name=param_name, 
            value=parameters[param_name], 
            request=new_request
        )
        db.session.add(new_parameter)
    group_items = data.get('groups')
    for group_item in group_items:
        group_id = group_item.get('id')
        group = Group.query.get(group_id)
        if not group:
            # Если нет такой группы, то создаём
            group = Group(id=group_id, name=group_item.get('name'))
            db.session.add(group)
        received_group = ReceivedGroup(
            group=group, 
            request=new_request
        )
        db.session.add(received_group)

    db.session.commit()


def search_groups(groups: list, query: str) -> list:
    matched_groups = [group for group in groups if query.lower() in group['name'].lower()]
    return matched_groups

def get_user_groups(user_id: int) -> list:
    # Получение списка групп пользователя
    user_groups_response = requests.get(
        'https://api.vk.com/method/groups.get',
        params={
            'user_id': user_id,
            'access_token': ACCESS_TOKEN,
            'extended': 1,
            'v': '5.131'
        }
    ).json()

    result = []
    if 'response' in user_groups_response:
        user_groups = user_groups_response['response']['items']
        for group in user_groups:
            item = {
                'id': group['id'],
                'name': group['name']
            }
            result.append(item)
    return result

def get_friends_groups(user_id: int) -> list:
    # Получение списка друзей пользователя
    friends_response = requests.get(
        'https://api.vk.com/method/friends.get',
        params={
            'user_id': user_id,
            'access_token': ACCESS_TOKEN,
            'v': '5.131'
        }
    ).json()

    if 'response' in friends_response:
        friends = friends_response['response']['items']
        friends_groups = []
        # Устанавливаем значением текущего шага 2
        # т.к. мы уже отправили два запроса перед этим
        step = 2
        # Получение списка групп для каждого друга
        for friend_id in friends:
            friend_groups = get_user_groups(friend_id)
            friends_groups.extend(friend_groups)
            step += 1
            # После каждого пятого запроса ждём секунду чтобы
            # не встретиться с ограничением 5 запросов в секунду
            if step % 5 == 0:
                time.sleep(1)

        return friends_groups

    return []

def paginate_result(data: list, page: int, per_page: int) -> list:
    start = (page - 1) * per_page
    end = start + per_page
    return data[start:end]

def construct_response(data):
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    response = Response(json_data, content_type='application/json; charset=utf-8')
    return response

      
if __name__ == '__main__':
    app.run()