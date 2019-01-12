# Constants
UPDATE_THREAD = False

# Supporting
from pprint import pprint

# Flask Main
from flask import render_template, redirect, url_for, flash
from flask import current_app, request
from flask import jsonify, abort
from flask import Response
# Flask Extension
from main import login_manager
from flask_login import login_user, current_user, logout_user, login_required as login_required2
# SQLAlchemy
from sqlalchemy import and_, or_
# Directory
from main import app, db, bcrypt
from main.forms import StallRegistrationForm, StallLoginForm, UserRegistrationForm, UserLoginForm, StallProfileUpdateForm
from main.models import BankAccount, User, Stall, Food, FoodOrder

# Misc
import os
import re
import base64
import secrets
from PIL import Image
import urllib
import threading
import time
from datetime import datetime

# Global Variables
status_map_time = {
    'Requested' : 'time_of_request',
    'Accepted' : 'time_of_acceptance',
    'Ready' : 'time_of_ready',
    'Fulfiled' : 'time_of_fulfilment',
    'Rejected' : 'time_of_failure',
    'Cancelled' : 'time_of_failure',
    'Withdrawn' : 'time_of_withdrawal',
    'Removed' : 'time_of_failure'
}

# Edited Functions
from functools import wraps
def login_required(*args2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.has_role(args2):
                return login_required2(func)(*args, **kwargs)
            else:
                return current_app.login_manager.unauthorized()
        return wrapper
    if isinstance(args2[0], type(lambda:None)):        
        return login_required2(args2[0])
    else:
        return decorator

# More Functions
def cvt2dict(data):
    new_data = data.decode('utf-8').replace('+', ' ')
    data_dict = {}
    for item in new_data.split('&'):
        key, value = item.split('=')
        key = urllib.parse.unquote(key)
        value = urllib.parse.unquote(value)
        data_dict[key] = value
    return data_dict

def string_isint(string):
    #return re.compile('\d+').match(string).span() == (0, len(string))
    try:
        int(string)
    except:
        return False
    else:
        return True

def string_isfloat(string):
    #return re.compile('\d+\.\d+').match(string).span() == (0, len(string))
    try:
        float(string)
    except:
        return False
    else:
        return True

# Refresh Nav & Content Data
stalls = Stall.query.all()
class UpdateDataThread(threading.Thread):
    def __init__(self, duration):
        super().__init__()
        self.duration = duration

    def run(self):
        global stalls
        while True:
            stalls = Stall.query.all()
            time.sleep(self.duration)

update_data_thread = UpdateDataThread(2)
if UPDATE_THREAD: update_data_thread.start()

# Routes
@app.route('/')
def index():
    return 'Hello World'

@app.route('/worker', methods=['POST'])
def service_worker():
    return Response(url_for('static', filename='sw.js'), mimetype='text/javascript')

@app.route('/user/auth/register', methods=['GET','POST'])
def user_register():
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(user_name=form.user_name.data, bank_account_no=form.bank_account_no.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_login'))

    global stalls
    return render_template('user/auth/register.html', form=form, stalls=stalls, current_user=current_user, title='Register')

@app.route('/user/auth/login', methods=['GET','POST'])
def user_login():
    if current_user.is_authenticated:
        redirect(url_for('home'))

    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.user_name.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid Username or Password')

    global stalls
    return render_template('user/auth/login.html', form=form, stalls=stalls, current_user=current_user, title='Login')

@app.route('/user/auth/logout')
def user_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    global stalls
    return render_template('user/main/home.html', stalls=stalls, current_user=current_user, title='Order @ FoodClub!')

@app.route('/menu/<int:stall_id>', methods=['GET','POST'])
def menu(stall_id):
    global stalls
    stall = Stall.query.get_or_404(stall_id)
    menu = stall.menu
    if request.method == 'POST':
        data = request.json
        print('=============================================================')
        print('POST JSON_DATA:')
        pprint(data)
        print('=============================================================')
        if data['Action'] == 'Ready Time':
            stall_orders = FoodOrder.query.filter(and_(FoodOrder.status == 'Accepted', FoodOrder.food_id.in_([food.food_id for food in menu])))

            total = 0
            for stall_order in stall_orders:        
                food = Food.query.get(stall_order.food_id)
                total += food.preperation_time

            return jsonify({
                'Status' : 'Success',
                'Ready Time' : str(total)
            })
        
        return jsonify({
            'Status' : 'Failure'
        })
    
    return render_template('user/main/menu.html', stalls=stalls, menu = menu, title=f'{stall.stall_name} Menu')

@app.route('/order/<int:food_id>', methods=['POST'])
def order(food_id):
    if current_user.has_role(['Stall']):
        logout_user()
    
    if current_user.is_anonymous:
        flash('Please sign in to order!')
        return jsonify({
            'Status' : 'Redirect', 
            'URL' : url_for('user_login')
        })
    
    food = Food.query.get_or_404(food_id)
    food_order = FoodOrder(user_id=current_user.user_id, food_id=food.food_id, status='Requested', time_of_request=datetime.utcnow())

    db.session.add(food_order)
    db.session.commit()

    return jsonify({'Status' : 'Success'})

@app.route('/query', methods=['POST'])
@login_required('User')
def user_query():
    # print(request.get_data())
    # data = cvt2dict(request.get_data())
    data = request.json
    print('=============================================================')
    print('POST JSON_DATA:')
    pprint(data)
    print('=============================================================')

    if data['Action'] == 'Orders':
        global status_map_time
        new_orders = []

        last_update_time = data.get('Last Update Time')
        update_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        if last_update_time:
            orders = FoodOrder.query.filter(FoodOrder.user_id == current_user.user_id).all()

            previous_time = datetime.strptime(last_update_time, '%Y-%m-%d %H:%M:%S.%f')

            for order in orders:
                order_status_time = getattr(order, status_map_time[order.status])

                if order.status == 'Accepted':
                    order_withdrawal_time = order.time_of_withdrawal
                    if order_withdrawal_time:
                        if order_withdrawal_time > order_status_time:
                            order_status_time = order_withdrawal_time

                if order_status_time >= previous_time:        
                    new_order = {
                        'Order ID' : order.order_id,
                        'Status' : order.status,
                        'Food ID' : order.food_id
                    }
                    new_orders.append(new_order)
        else:
            orders = FoodOrder.query.filter(and_(FoodOrder.user_id == current_user.user_id, FoodOrder.status.in_(['Requested','Accepted','Ready']))).all()
            for order in orders:
                new_order = {
                    'Order ID' : order.order_id,
                    'Status' : order.status,
                    'Food ID' : order.food_id
                }
                new_orders.append(new_order)
        
        return jsonify({
            'Status' : 'Success',
            'New Orders' : new_orders,
            'Update Time' : update_time
        })

    elif data['Action'] == 'Food':
        food_id_list = data.get('Food ID List')
        
        food_data_list = []
        for food_id in food_id_list:
            food = Food.query.get_or_404(food_id)

            stall = food.stall

            food_data = {
                'Food ID' : food_id,
                'Food Name' : food.food_name,
                'Stall Name' : stall.stall_name
            }
            food_data_list.append(food_data)

        return jsonify({
            'Status' : 'Success',
            'Food Data List' : food_data_list
        })

    return jsonify({
        'Status' : 'Failure'
    })

@app.route('/user/history', methods=['GET','POST'])
def user_history():
    if request.method == 'POST':
        data = request.json
        print('=============================================================')
        print('POST JSON_DATA:')
        pprint(data)
        print('=============================================================')
        if data['Action'] == 'Ready Time':
            order_id = data['Order ID']
            if order_id is None:
                return jsonify({
                    'Status' : 'Failure'
                })

            order_id = data.get('Order ID')
            order = FoodOrder.query.get_or_404(order_id)

            if order.user_id != current_user.user_id: abort(403)
            if order.status != 'Accepted':
                return jsonify({
                    'Status' : 'Failure'
                })
            
            food = Food.query.get(order.food_id)
            stall = food.stall
            stall_orders = FoodOrder.query.filter(and_(FoodOrder.status == 'Accepted', FoodOrder.food_id.in_([food.food_id for food in stall.menu])))

            if order in stall_orders:
                total = 0
                for stall_order in stall_orders:
                    if stall_order == order:
                        break
                    else:
                        food2 = Food.query.get(stall_order.food_id)
                        total += food2.preperation_time
                
                return jsonify({
                    'Status' : 'Success',
                    'Ready Time' : str(total)
                })
            else:
                print('Code: User History -1')
                return jsonify({
                    'Status' : 'Failure'
                })
                
        elif data['Action'] == 'Remove':
            order_id = data.get('Order ID')
            order = FoodOrder.query.get_or_404(order_id)
            if order.user_id != current_user.user_id: abort(403)
            if order.status != 'Requested': 
                return jsonify({
                    'Status' : 'Failure'
                })
            
            order.status = 'Removed'
            order.time_of_failure = datetime.utcnow()
            db.session.commit()

            return jsonify({
                'Status' : 'Success'
            })

    global stalls
    return render_template('user/main/order-history.html', stalls=stalls, current_user=current_user, title='Order History')

@app.route('/stall/auth/register', methods = ['GET', 'POST'])
def stall_register():
    if current_user.is_authenticated:
        return redirect(url_for('stall_dashboard'))
    form = StallRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        stall = Stall(stall_name = form.stall_name.data, bank_account_no = form.bank_account_no.data, password = hashed_password)
        db.session.add(stall)
        db.session.commit()
        global stalls
        stalls = Stall.query.all()
        return redirect(url_for('stall_login'))
    return render_template('stall/auth/register.html', form = form, current_user=current_user, title='Register')

@app.route('/stall/auth/login', methods = ['GET','POST'])
def stall_login():
    if current_user.is_authenticated:
        return redirect(url_for('stall_dashboard'))
    form = StallLoginForm()
    if form.validate_on_submit():
        stall = Stall.query.filter_by(stall_name = form.stall_name.data).first()
        if stall and bcrypt.check_password_hash(stall.password, form.password.data):
            login_user(stall)
            return redirect(url_for('stall_dashboard'))
        else:
            flash('Invalid Stall Name or Password')

    return render_template('stall/auth/login.html', form = form, current_user=current_user, title='Login')

@app.route('/stall/auth/logout')
def stall_logout():
    logout_user()
    return redirect(url_for('stall_login'))

@app.route('/stall/dashboard')
@login_required('Stall')
def stall_dashboard():
    # return 'This is a dashboard'
    return redirect(url_for('stall_menu'))

@app.route('/stall/menu', methods = ['GET','POST'])
@login_required('Stall')
def stall_menu():
    if request.method == 'POST':
        #print(request.get_data())
        # data = cvt2dict(request.get_data())
        data = request.json
        print('=============================================================')
        print('POST JSON_DATA:')
        pprint(data)
        print('=============================================================')

        if data['Action'] == 'Add':
            food_name = data.get('Food Name')
            price = data.get('Price')
            calorie = data.get('Calorie')
            preperation_time = data.get('Preperation Time')
            description = data.get('Description')
            image_data = data.get('Image Data')            

            error = None

            if not all((food_name, price, calorie, preperation_time)):
                error = 'Some Data is Missing'
            elif len(food_name) > 30:
                error = 'Food Name exceeds 30 Characters'
            elif len(description) > 200:
                error = 'Description exceeds 200 Characters'            
            elif not string_isfloat(price):
                error = 'Price is not numeric'
            elif not 0 <= float(price) <= 99.99:
                error = 'Price must be between $0.00 to $99.99'
            elif not string_isint(calorie):
                error = 'Calorie is not an integer'
            elif not 0 <= int(calorie) <= 9999:
                error = 'Calorie must be between 0 to 9999'
            elif not string_isfloat(preperation_time):
                error = 'Preperation Time is not numeric'
            elif not 0 <= float(preperation_time) <= 99:
                error = 'Preperation Time must be between 0 mins to 99 mins'
            elif image_data:
                # Extract Image Properties if image exists
                file_type, file_extension, file_encoding, file_data = re.compile('data:(\w+)/(\w+);(\w+),(.+)').split(image_data)[1:-1]
                if not (file_type == 'image' and file_extension in ['png','jpeg','webp'] and file_encoding == 'base64'):
                    error = 'File data is invalid.'
            
            if error:
                return jsonify({
                    'Status' : 'Failure',
                    'Error' : error
                })

            if image_data:            
                # Generate Image File Name
                random_hex = secrets.token_hex(8)
                image_file_name = random_hex + '.' + file_extension
                # Creating Image
                image_file_path = os.path.join(app.root_path, 'static/images/food-pictures', image_file_name)
                with open(image_file_path, 'wb') as pic_file:
                    pic_file.write(base64.b64decode(file_data))

                new_image = Image.open(image_file_path)
                new_image.thumbnail((434,280))
                new_image.save(image_file_path)

            else:
                image_file_name = 'default.webp'

            # Updating DB
            food = Food(
                stall_id = current_user.stall_id, 
                food_name = data['Food Name'], 
                price = data['Price'], 
                calorie = data['Calorie'], 
                preperation_time = data['Preperation Time'], 
                description = data['Description'],
                food_pic = image_file_name
            )

            db.session.add(food)
            db.session.commit()
            
            return jsonify({
                'Status' : 'Success',
                'Food ID' : food.food_id,
                'Food Name' : food.food_name,
                'Price' : str(food.price),
                'Calorie' : food.calorie,
                'Preperation Time' : str(food.preperation_time),
                'Description' : food.description,
                'Image Data' : url_for('static', filename = r'images/food-pictures/' + food.food_pic)
            })
        elif data['Action'] == 'Update':
            food_id = data.get('Food ID')
            food_name = data.get('Food Name')
            price = data.get('Price')
            calorie = data.get('Calorie')
            preperation_time = data.get('Preperation Time')
            description = data.get('Description')
            image_data = data.get('Image Data')

            food = Food.query.get_or_404(food_id)
            if food.stall != current_user:
                abort(403)

            error = None

            if food_name and len(food_name) > 30:
                error = 'Food Name exceeds 30 Characters'
            elif description and len(description) > 200:
                error = 'Description exceeds 200 Characters'
            elif price and not string_isfloat(price):
                error = 'Price is not numeric'
            elif price and not 0 <= float(price) <= 99.99:
                error = 'Price must be between $0.00 to $99.99'
            elif calorie and not string_isint(calorie):
                error = 'Calorie is not an integer'
            elif calorie and not 0 <= int(calorie) <= 9999:
                error = 'Calorie must be between 0 to 9999'
            elif preperation_time and not string_isfloat(preperation_time):
                error = 'Preperation Time is not numeric'
            elif preperation_time and not 0 <= float(preperation_time) <= 99:
                error = 'Preperation Time must be between 0 mins to 99 mins'
            elif image_data:
                # Extract Image Properties if image exists
                file_type, file_extension, file_encoding, file_data = re.compile('data:(\w+)/(\w+);(\w+),(.+)').split(image_data)[1:-1]
                if not (file_type == 'image' and file_extension in ['png','jpeg','webp'] and file_encoding == 'base64'):
                    error = 'File data is invalid'            

            if error:
                return jsonify({
                    'Status' : 'Failure',
                    'Error' : error
                })

            updated_food_items = {}

            if food_name:
                food.food_name = food_name
                updated_food_items['Food Name'] = food.food_name
            if price:
                food.price = price
                updated_food_items['Price'] = str(food.price)
            if calorie:
                food.calorie = calorie
                updated_food_items['Calorie'] = food.calorie
            if preperation_time:
                food.preperation_time = preperation_time
                updated_food_items['Preperation Time'] = str(food.preperation_time)
            if description is not None:
                food.description = description
                updated_food_items['Description'] = food.description
            if image_data:
                if food.food_pic == 'default.webp':
                    # Generate Image File Name
                    random_hex = secrets.token_hex(8)
                    image_file_name = random_hex + '.' + file_extension
                    food.food_pic = image_file_name
                else:
                    image_file_name = food.food_pic
                
                # Creating Image
                image_file_path = os.path.join(app.root_path, r'static/images/food-pictures', image_file_name)
                with open(image_file_path, 'wb') as pic_file:
                    pic_file.write(base64.b64decode(file_data))
                
                new_image = Image.open(image_file_path)
                new_image.thumbnail((434,280))
                new_image.save(image_file_path)

                updated_food_items['Image Data'] = url_for('static', filename = r'images/food-pictures' + food.food_pic)

            db.session.commit()

            updated_food_items['Status'] = 'Success'
            
            return jsonify(updated_food_items)
            
        elif data['Action'] == 'Remove':
            food_id = data.get('Food ID')

            food = Food.query.get_or_404(food_id)
            if food.stall != current_user:
                abort(403)

            if food.food_pic != 'default.webp':
                image_file_path = os.path.join(app.root_path, 'static/images/food-pictures/', food.food_pic)
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)

            db.session.delete(food)
            db.session.commit()

            return jsonify({'Status' : 'Success'})

        elif data['Action'] == 'Retrieve':
            food_list = []

            menu = current_user.menu
            for food in menu:
                food_item = {
                    'Food ID' : food.food_id,
                    'Food Name' : food.food_name,
                    'Price' : str(food.price),
                    'Calorie' : food.calorie,
                    'Preperation Time' : str(food.preperation_time),
                    'Description' : food.description,
                    'Image Data' : url_for('static', filename = r'images/food-pictures/' + food.food_pic)}
                food_list.append(food_item)
            
            return jsonify({
                'Status' : 'Success',
                'Food List' : food_list
            })

        return jsonify({
            'Status' : 'Failure',
            'Error' : 'Request Method is not allowed'
        })

    return render_template('stall/main/stall-menu.html', current_user=current_user, title='Menu')

@app.route('/stall/orders', methods = ['GET','POST'])
@login_required('Stall')
def stall_orders():
    if request.method == 'POST':
        #print(request.get_data())
        # data = cvt2dict(request.get_data())
        data = request.json
        print('=============================================================')
        print('POST JSON_DATA:')
        pprint(data)
        print('=============================================================')

        request_action = data['Action'].split(' ')

        if len(request_action) != 2:
            return jsonify({
                'Status' : 'Failure'
            })

        if request_action[0] == 'Retrieve':
            if request_action[1] == 'Incoming':
                orders = FoodOrder.query.filter(and_(FoodOrder.food_id.in_([food.food_id for food in current_user.menu]), FoodOrder.status == 'Requested')).all()

            elif request_action[1] == 'Accepted':
                orders = FoodOrder.query.filter(and_(FoodOrder.food_id.in_([food.food_id for food in current_user.menu]), FoodOrder.status == 'Accepted')).all()

            elif request_action[1] == 'Completed':
                orders = FoodOrder.query.filter(and_(FoodOrder.food_id.in_([food.food_id for food in current_user.menu]), FoodOrder.status == 'Ready')).all()
            
            else:
                return jsonify({
                    'Status' : 'Failure'
                })

            new_orders = []
            for order in orders:
                food = Food.query.get(order.food_id)
                new_order = {
                    'Food Name' : food.food_name,
                    'Order ID' : order.order_id,
                }
                new_orders.append(new_order)
            
            return jsonify({
                'Status' : 'Success',
                request_action[1] : new_orders
            })
        else:
            order_id = data['Order ID']

            food_order = FoodOrder.query.get_or_404(order_id)

            food = Food.query.get(food_order.food_id)

            if food.stall != current_user:
                return jsonify({
                    'Status' : 'Failure'
                })

            if request_action[1] == 'Incoming' and food_order.status == 'Requested':
                if request_action[0] == 'Accept':
                    food_order.status = 'Accepted'                    
                    food_order.time_of_acceptance = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Food Name' : food.food_name,
                        'Order ID' : food_order.order_id                        
                    })
                elif request_action[0] == 'Reject':
                    food_order.status = 'Rejected'                    
                    food_order.time_of_failure = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Order ID' : order_id
                    })
            elif request_action[1] == 'Accepted' and food_order.status == 'Accepted':
                if request_action[0] == 'Accept':
                    food_order.status = 'Ready'                    
                    food_order.time_of_ready = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Food Name' : food.food_name,
                        'Order ID' : food_order.order_id
                    })
                elif request_action[0] == 'Reject':
                    food_order.status = 'Cancelled'
                    food_order.time_of_failure = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Order ID' : order_id
                    })
            elif request_action[1] == 'Completed' and food_order.status == 'Ready':
                if request_action[0] == 'Accept':
                    food_order.status = 'Fulfiled'
                    food_order.time_of_fulfilment = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Order ID' : food_order.order_id 
                    })
                elif request_action[0] == 'Reject':
                    food_order.status = 'Accepted'
                    # food_order.time_of_ready = None
                    food_order.time_of_withdrawal = datetime.utcnow()
                    db.session.commit()
                    return jsonify({
                        'Status' : 'Success',
                        'Food Name': food.food_name,
                        'Order ID' : order_id
                    })
        
        return jsonify({
            'Status' : 'Failure'
        })

    return render_template('stall/main/stall-orders.html', current_user=current_user, title='Orders')

def save_form_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images/stall-pictures', picture_fn)
    form_picture.save(picture_path)

    return picture_fn

@app.route('/stall/settings', methods=['GET','POST'])
@login_required('Stall')
def stall_settings():
    form = StallProfileUpdateForm()
    if form.validate_on_submit():
        if form.stall_pic.data:
            if current_user.stall_pic != 'default.webp':
                os.remove(url_for('static', filename='images/stall-pictures/' + current_user.stall_pic))
            stall_pic_fn = save_form_picture(form.stall_pic.data)
            current_user.stall_pic = stall_pic_fn
        current_user.stall_name = form.stall_name.data
        current_user.bank_account_no = form.bank_account_no.data
        db.session.commit()
        flash('Your Profile Info has been updated!')
        stalls = Stall.query.all()
    elif request.method == 'GET':
        form.stall_name.data = current_user.stall_name
        form.bank_account_no.data = current_user.bank_account_no
        
    return render_template('stall/main/stall-settings.html', form=form, current_user=current_user, title='Settings')


@login_manager.unauthorized_handler
def unauthorized():
    if current_user.is_anonymous:
        if request.method == 'GET':
            return redirect(url_for('user_login'))
        elif request.method == 'POST':
            return jsonify({'Status' : 'Failure'})
    elif current_user.has_role(['Stall']):
        if request.method == 'GET':
            return redirect(url_for('stall_dashboard'))
        elif request.method == 'POST':
            return jsonify({'Status' : 'Failure'})
    elif current_user.has_role(['User']):
        if request.method == 'GET':
            return redirect(url_for('home'))
        elif request.method == 'POST':
            return jsonify({'Status' : 'Failure'})
    else:
        return 'Error 404 :('
        