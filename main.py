from audioop import reverse
from distutils.log import error
import random
from flask import Flask, render_template, request, redirect
from google.cloud import datastore
from google.auth.transport import requests
import google.oauth2.id_token
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./python-application-347701-9536203a9925.json"

app = Flask(__name__, template_folder='templates')

datastore_client = datastore.Client()

firebase_request_adapter = requests.Request()


def createUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'email': claims['email'],
        # 'name': claims['name'],
        'car_list': []
    })
    datastore_client.put(entity)


def retrieveUserInfo(claims):
    entity_key = datastore_client.key('UserInfo', claims['email'])
    entity = datastore_client.get(entity_key)
    return entity


def retrieveCars(user_info):
    # make key objects out of all the keys and retrieve them
    car_ids = user_info['car_list']
    print(car_ids)
    car_keys = []
    for i in range(len(car_ids)):
        car_keys.append(datastore_client.key('Cars', car_ids[i]))
    car_list = datastore_client.get_multi(car_keys)
    return car_list


def createMyCar(claims, name, manufacturer, year, battery_size, WLTP_range, cost, power):
    entity = datastore.Entity()
    # name, manufacturer, year, battery size (Kwh), WLTP range
    # (Km), cost, power (Kw)
    id = random.getrandbits(63)
    entity_key = datastore_client.key('Cars', id)
    entity = datastore.Entity(key=entity_key)
    entity.update({
        'name': name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'WLTP_range': WLTP_range,
        'cost': cost,
        'power': power,
        'review_list': [],
        'average_reviews': 0
    })
    datastore_client.put(entity)
    return id


def addCarToUser(user_info, id):
    address_keys = user_info['car_list']
    address_keys.append(id)
    user_info.update({
        'car_list': address_keys
    })
    datastore_client.put(user_info)


def deleteCar(claims, id):
    user_info = retrieveUserInfo(claims)
    car_list_keys = user_info['car_list']
    car_id = None
    for index, idx in enumerate(car_list_keys):
        if car_list_keys[index] == id:
            car_id = index
    print(car_id)
    car_key = datastore_client.key('Cars', car_list_keys[car_id])
    datastore_client.delete(car_key)
    del car_list_keys[car_id]
    user_info.update({
        'car_list': car_list_keys
    })
    datastore_client.put(user_info)


def editCarInfo(claims, id):
    user_info = retrieveUserInfo(claims)
    car_list_keys = user_info['car_list']
    car_id = None
    for index, idx in enumerate(car_list_keys):
        if car_list_keys[index] == id:
            car_id = index
    print(car_id)
    car_key = datastore_client.key('Cars', car_list_keys[car_id])
    car = datastore_client.get(car_key)
    return car


def updateCarInfo(id, name, manufacturer, year, battery_size, WLTP_range, cost, power):
    car_key = datastore_client.key('Cars', id)
    car = datastore_client.get(car_key)
    car.update({
        'id': id,
        'name': name,
        'manufacturer': manufacturer,
        'year': year,
        'battery_size': battery_size,
        'WLTP_range': WLTP_range,
        'cost': cost,
        'power': power,
    })
    datastore_client.put(car)


def retriveSingleCarInfo(id):
    car_key = datastore_client.key('Cars', id)
    car = datastore_client.get(car_key)
    return car


def createReview(name, text, rating):
    entity = datastore.Entity()
    entity.update({
        'name': name,
        'text': text,
        'rating': rating,
    })
    return entity


def addReviewToCar(car_info, review_entity):
    reviews = car_info['review_list']
    reviews.append(review_entity)
    car_info.update({
        'review_list': reviews
    })
    datastore_client.put(car_info)


def getAverageReview(review_list):
    avg_review = 0
    for i in review_list:
        avg_review += i
    avg = avg_review/len(review_list)
    return round(avg, 1)


def addAverageToCar(car_info, average_rating):
    car_info.update({
        'average_reviews': average_rating
    })
    datastore_client.put(car_info)


@ app.route('/')
def root():
    result = None
    error_message = 'No Cars to Show!'
    query = datastore_client.query(kind='Cars')
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_name', methods=['POST'])
def search_by_car_name():
    name = request.form['car_name']
    error_message = 'No Cars to Show!'
    if(request.form['car_name'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('name', '=', name)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_power', methods=['POST'])
def search_by_car_power():
    power = request.form['car_power']
    error_message = 'No Cars to Show!'
    if(request.form['car_power'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('power', '=', power)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_WLTP_range', methods=['POST'])
def search_by_car_WLTP_range():
    WLTP_range = request.form['car_WLTP_range']
    error_message = 'No Cars to Show!'
    if(request.form['car_WLTP_range'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('WLTP_range', '=', WLTP_range)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_battery_size', methods=['POST'])
def search_by_car_battery_size():
    battery_size = request.form['car_battery_size']
    error_message = 'No Cars to Show!'
    if(request.form['car_battery_size'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('battery_size', '=', battery_size)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_manufacturer', methods=['POST'])
def search_by_car_manufacturer():
    manufacturer = request.form['car_manufacturer']
    error_message = 'No Cars to Show!'
    if(request.form['car_manufacturer'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('manufacturer', '=', manufacturer)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@app.route('/search_by_year', methods=['POST'])
def search_by_car_year():
    year = request.form['car_year']
    error_message = 'No Cars to Show!'
    if(request.form['car_year'] == ''):
        return redirect('/')
    query = datastore_client.query(kind='Cars')
    query.add_filter('year', '=', year)
    result = list(query.fetch())
    return render_template('index.html', data=result, error_message=error_message)


@ app.route('/login')
def login():
    name = 'Login'
    return render_template('login.html', name=name)


@ app.route('/signup')
def signup():
    name = 'Sign - Up'
    return render_template('signup.html', name=name)


@ app.route('/profile')
def profile():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    cars = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            print(claims)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            print(user_info)
            cars = retrieveCars(user_info)
        except ValueError as exc:
            error_message = str(exc)
    return render_template('profile.html', user_data=claims, error_message=error_message, user_info=user_info, cars=cars)


@ app.route('/createEvCar')
def createCar():
    error_message = None
    return render_template('createEcar.html', error_message=error_message)


@ app.route('/createEvCar', methods=['POST'])
def addCars():
    id_token = request.cookies.get("token")
    claims = None
    user_info = None
    car_list = None
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            query = datastore_client.query(kind='Cars')
            result = list(query.fetch())
            name = request.form['car-name']
            manufacturer = request.form['car-manufacturer']
            year = request.form['car-year']
            battery_size = request.form['car-battery']
            wltp_range = request.form['car-WLTP-range']
            cost = request.form['car-cost']
            power = request.form['car-power']
            for car in result:
                if name == car['name'] and year == car['year'] and manufacturer == car['manufacturer']:
                    error_message = 'Car with same credintial already exist!'
                    return render_template('createEcar.html', error_message=error_message)

            # name, manufacturer, year, battery size (Kwh), WLTP range
            # (Km), cost, power (Kw)
            id = createMyCar(claims, name, manufacturer, year, battery_size,
                             wltp_range, cost, power)
            addCarToUser(user_info, id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/car/<int:id>')
def carInfo(id):
    car = retriveSingleCarInfo(id)
    id_token = request.cookies.get("token")
    claims = None
    user_info = None
    reverse_review_list = []
    car_id_list = []
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            car_id_list = user_info['car_list']
            print('Hello')
        except ValueError as exc:
            error_message = str(exc)
    reverse_review_list = sorted(
        car['review_list'], key=lambda d: d['rating'])
    return render_template('carInfo.html', car=car, car_id_list=car_id_list, user_info=user_info, reverse_review_list=reverse_review_list)


@app.route('/editCar/<int:id>')
def editCar(id):
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    user_info = None
    cars = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            if user_info == None:
                createUserInfo(claims)
                user_info = retrieveUserInfo(claims)
            print(user_info['car_list'])
            if id in user_info['car_list']:
                print('ok')
                car = editCarInfo(claims, id)
            else:
                return redirect('/')
        except ValueError as exc:
            error_message = str(exc)
    return render_template('editCar.html', car=car, user_info=user_info)


@app.route('/editCar/<int:id>', methods=['POST'])
def updateEditCar(id):
    id_token = request.cookies.get("token")
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)

            # name, manufacturer, year, battery size (Kwh), WLTP range
            # (Km), cost, power (Kw)
            name = request.form['car-name']
            manufacturer = request.form['car-manufacturer']
            year = request.form['car-year']
            battery_size = request.form['car-battery']
            wltp_range = request.form['car-WLTP-range']
            cost = request.form['car-cost']
            power = request.form['car-power']
            query = datastore_client.query(kind='Cars')
            updateCarInfo(id, name, manufacturer, year, battery_size,
                          wltp_range, cost, power)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@ app.route('/delete_car/<int:id>', methods=['POST'])
def deleteCarFromUser(id):
    id_token = request.cookies.get("token")
    error_message = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            print(id)
            deleteCar(claims, id)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/car/<int:id>', methods=['POST'])
def addReview(id):
    id_token = request.cookies.get("token")
    claims = None
    user_info = None
    car = None
    review = None
    average_review = None
    review_list = []
    car_id_list = []
    reverse_review_list = []
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(id_token,
                                                                  firebase_request_adapter)
            user_info = retrieveUserInfo(claims)
            car_id_list = user_info['car_list']
            print(car_id_list)
            car = retriveSingleCarInfo(id)
            text = request.form['text']
            rating = request.form['rating']
            email = user_info['email']
            print('Hello')
            review = createReview(email, text, rating)
            addReviewToCar(car, review)
            for i in car['review_list']:
                review_list.append(int(i['rating']))
            average_review = getAverageReview(review_list)
            addAverageToCar(car, average_review)

        except ValueError as exc:
            error_message = str(exc)
    reverse_review_list = sorted(
        car['review_list'], key=lambda d: d['rating'])
    return render_template('carInfo.html', car=car, car_id_list=car_id_list, user_info=user_info, reverse_review_list=reverse_review_list)


@ app.route('/compare')
def compareCars():
    return render_template('compare.html')


@ app.route('/compare/cars')
def listOfCars():
    result = None
    car_select_message = None
    error_message = 'Nothing To Compare'
    query = datastore_client.query(kind='Cars')
    result = list(query.fetch())
    return render_template('listOfCars.html', car_select_message=car_select_message, data=result, length_of_list=len(result), error_message=error_message)


@ app.route('/compare/cars', methods=['POST'])
def listOfcarsSubmit():
    car_list = []
    compare_list = []
    float_list = []
    error_message = None
    car_select_message = None
    result = request.form.getlist('car-list')
    if len(result) == 1:
        query = datastore_client.query(kind='Cars')
        result = list(query.fetch())
        car_select_message = 'Please select two or more cars to compare!'
        return render_template('listOfCars.html', car_select_message=car_select_message, data=result, length_of_list=len(result), error_message=error_message)
    # print(result)
    for carId in result:
        car_list.append(retriveSingleCarInfo(int(carId)))
    for index, carItem in enumerate(car_list):
        compare_list.append(dict(car_list[index]))
    # print(compare_list)
    selectedKeys = list()
    for carItem in compare_list:
        for key, values in carItem.items():
            if key == 'name' or key == 'manufacturer' or key == 'review_list':
                selectedKeys.append(key)

    for key in selectedKeys:
        for carItem in compare_list:
            if key in carItem:
                del carItem[key]
    float_list = [dict([a, float(x)] for a, x in b.items())
                  for b in compare_list]

    min_cost = min(item['cost'] for item in float_list)
    max_cost = max(item['cost'] for item in float_list)
    max_Wltp_range = max(item['WLTP_range'] for item in float_list)
    min_Wltp_range = min(item['WLTP_range'] for item in float_list)
    max_power = max(item['power'] for item in float_list)
    min_power = min(item['power'] for item in float_list)
    max_battery_size = max(item['battery_size'] for item in float_list)
    min_battery_size = min(item['battery_size'] for item in float_list)
    min_average_rating = min(item['average_reviews'] for item in float_list)
    max_average_rating = max(item['average_reviews'] for item in float_list)

    return render_template('compare.html', car_list=car_list, min_cost=min_cost,
                           max_cost=max_cost, max_wltp_range=max_Wltp_range, min_wltp_range=min_Wltp_range,
                           max_power=max_power, min_power=min_power, max_battery_size=max_battery_size,
                           min_battery_size=min_battery_size, max_average_rating=max_average_rating,
                           min_average_rating=min_average_rating)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
