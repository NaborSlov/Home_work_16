import json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class User(db.Model):
    """
    Модель пользователя
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    age = db.Column(db.Integer)
    email = db.Column(db.String(100))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(15))


class Order(db.Model):
    """
    Модель заказов
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    address = db.Column(db.String)
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Offer(db.Model):
    """
    Модель предложений
    """
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# создаем таблицы на основе моделей
db.create_all()

# наполняем таблицу с пользователями
with open('users.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)
    users = [User(
        id=item['id'],
        first_name=item['first_name'],
        last_name=item['last_name'],
        age=item['age'],
        email=item['email'],
        role=item['role'],
        phone=item['phone']
    ) for item in data]

# наполняем таблицу с заказами
with open('orders.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)
    orders = [Order(
        id=item['id'],
        name=item['name'],
        description=item['description'],
        start_date=item['start_date'],
        end_date=item['end_date'],
        address=item['address'],
        price=item['price'],
        customer_id=item['customer_id'],
        executor_id=item['executor_id']
    ) for item in data]

# наполняем таблицу с предложениями
with open('offers.json', 'r', encoding='UTF-8') as file:
    data = json.load(file)
    offers = [Offer(
        id=item["id"],
        order_id=item["order_id"],
        executor_id=item["executor_id"]
    ) for item in data]

# сохраняем данные
with db.session.begin():
    db.session.add_all(users)
    db.session.add_all(orders)
    db.session.add_all(offers)


def serialize_json_user(item):
    """
    Для сериализации данных из таблицы User
    """
    return {
        'id': item.id,
        'first_name': item.first_name,
        'last_name': item.last_name,
        'age': item.age,
        'email': item.email,
        'role': item.role,
        'phone': item.phone
    }


def serialize_json_order(item):
    """
    Для сериализации данных из таблицы Order
    """
    return {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'start_date': item.start_date,
        'end_date': item.end_date,
        'address': item.address,
        'price': item.price,
        'customer_id': item.customer_id,
        'executor_id': item.executor_id
    }


def serialize_json_offer(item):
    """
    Для сериализации данных из таблицы Offer
    """
    return {
        'id': item.id,
        'order_id': item.order_id,
        'executor_id': item.executor_id
    }


@app.route('/users', methods=['GET', 'POST'])
def get_all_users():
    """
    Представления для получения всех пользователей и добавления новых
    """
    # метод get для получения всех пользователей
    if request.method == 'GET':
        users_data = db.session.query(User).all()
        return jsonify([serialize_json_user(user) for user in users_data])

    # метод пост для добавления новых пользователей
    if request.method == 'POST':
        # получения данных в виде json
        user_json = request.json
        # добавление нового пользователя
        db.session.add(User(
            first_name=user_json.get('first_name'),
            last_name=user_json.get('last_name'),
            age=user_json.get('age'),
            email=user_json.get('email'),
            role=user_json.get('role'),
            phone=user_json.get('phone')
        ))
        db.session.commit()
        db.session.close()
        # получения добавленного пользователя
        user = db.session.query(User).filter(User.first_name == user_json.get('first_name')).one()
        return serialize_json_user(user)


@app.route('/users/<int:index>', methods=['GET', 'PUT', 'DELETE'])
def get_one_user(index):
    """
    Плучение, обновление и удаление пользователя по его id
    """
    # получение пользователя по его id
    if request.method == 'GET':
        user = db.session.query(User).get(index)
        # проверка на наличие запрашиваемого пользователя
        if user is None:
            return "Такого пользователя нет"

        return serialize_json_user(user)

    # обновление данных пользователя
    if request.method == 'PUT':
        # получения данных в виде json
        user_data_update = request.json
        # получения пользователя которого нужно обновить
        user = db.session.query(User).get(index)
        # проверка на наличие запрашиваемого пользователя
        if user is None:
            return "Такого пользователя нет"
        # обновление данных
        user.first_name = user_data_update.get('first_name', user.first_name)
        user.last_name = user_data_update.get('last_name', user.last_name)
        user.age = user_data_update.get('age', user.age)
        user.email = user_data_update.get('email', user.email)
        user.role = user_data_update.get('role', user.role)
        user.phone = user_data_update.get('phone', user.phone)
        # обновление и сохранение данных
        db.session.add(user)
        db.session.commit()
        db.session.close()
        # вывод обновленного пользователя
        user_new = db.session.query(User).get(index)
        return serialize_json_user(user_new)
    # удаление пользователя по его id
    if request.method == 'DELETE':
        user = db.session.query(User).get(index)
        # проверка на наличие запрашиваемого пользователя
        if user is None:
            return "<h1>Такого пользователя нет</h1>"
        # удаление пользователя
        db.session.delete(user)
        db.session.commit()
        db.session.close()

        return f'<h1>Пользователь с id-{index} удален</h1>'


@app.route('/orders', methods=['GET', 'POST'])
def get_all_orders():
    """
    Представления для получения всех заказов и добавления новых
    """
    # получения заказа по его id
    if request.method == 'GET':
        orders_data = db.session.query(Order).all()
        return jsonify([serialize_json_order(order) for order in orders_data])
    # добавление нового заказа
    if request.method == 'POST':
        order_json = request.json

        db.session.add(Order(
            name=order_json.get('name'),
            description=order_json.get('description'),
            start_date=order_json.get('start_date'),
            end_date=order_json.get('end_date'),
            address=order_json.get('address'),
            price=order_json.get('price'),
            customer_id=order_json.get('customer_id'),
            executor_id=order_json.get('executor_id')
        ))
        db.session.commit()
        db.session.close()

        order = db.session.query(Order).filter(Order.first_name == order_json.get('name')).one()
        return serialize_json_user(order)


@app.route('/orders/<int:index>', methods=['GET', 'PUT', 'DELETE'])
def get_one_order(index):
    """
    Плучение, обновление и удаление заказа по его id
    """
    # получения заказа по его id
    if request.method == 'GET':
        order = db.session.query(Order).get(index)

        if order is None:
            return "Такого заказа нет"

        return serialize_json_order(order)
    # обновление данных заказа
    if request.method == 'PUT':
        order_data_update = request.json
        order = db.session.query(Order).get(index)

        if order is None:
            return "Такого заказа нет"

        order.name = order_data_update.get('name', order.name)
        order.description = order_data_update.get('description', order.description)
        order.start_date = order_data_update.get('start_date', order.start_date)
        order.end_date = order_data_update.get('end_date', order.end_date)
        order.address = order_data_update.get('address', order.address)
        order.price = order_data_update.get('price', order.price)
        order.customer_id = order_data_update.get('customer_id', order.customer_id)
        order.executor_id = order_data_update.get('executor_id', order.executor_id)

        db.session.add(order)
        db.session.commit()
        db.session.close()

        order_new = db.session.query(Order).get(index)
        return serialize_json_order(order_new)
    # удаление заказа
    if request.method == 'DELETE':
        order = db.session.query(Order).get(index)

        if order is None:
            return "<h1>Такого заказа нет</h1>"

        db.session.delete(order)
        db.session.commit()
        db.session.close()

        return f'<h1>Заказ с id-{index} удален</h1>'


@app.route('/offers', methods=['GET', 'POST'])
def get_all_offers():
    """
    Представления для получения всех офферов и добавления новых
    """
    # получения всех офферов
    if request.method == 'GET':
        offers_data = db.session.query(Offer).all()
        return jsonify([serialize_json_offer(offer) for offer in offers_data])
    # добавление новго оффера
    if request.method == 'POST':
        offer_json = request.json

        db.session.add(Order(
            order_id=offer_json.get('order_id'),
            executor_id=offer_json.get('executor_id'),
        ))
        db.session.commit()
        db.session.close()

        return "Данные добавлены"


@app.route('/offers/<int:index>', methods=['GET', 'PUT', 'DELETE'])
def get_one_offer(index):
    """
    Плучение, обновление и удаление оффера по его id
    """
    # получения оффера по его id
    if request.method == 'GET':
        offer = db.session.query(Offer).get(index)

        if offer is None:
            return "Такого оффера нет"

        return serialize_json_offer(offer)
    # обновление данных оффера
    if request.method == 'PUT':
        offer_data_update = request.json

        offer = db.session.query(Offer).get(index)

        if offer is None:
            return "Такого оффера нет"

        offer.order_id = offer_data_update.get('order_id', offer.order_id)
        offer.executor_id = offer_data_update.get('executor_id', offer.executor_id)

        db.session.add(offer)
        db.session.commit()
        db.session.close()

        return 'Данные добавлены'
    # удаление оффера по его id
    if request.method == 'DELETE':
        offer = db.session.query(Offer).get(index)

        if offer is None:
            return "<h1>Такого оффера нет</h1>"

        db.session.delete(offer)
        db.session.commit()
        db.session.close()

        return f'<h1>Offer с id-{index} удален</h1>'


if __name__ == "__main__":
    app.run(debug=True)
