#pylint: skip-file

from datetime import datetime
from main import db
from main import login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user_or_stall(session_id):
    if session_id:
        owner, owner_id = session_id.split(':')
        if owner == 'User':
            return User.query.get(owner_id)
        elif owner == 'Stall':
            return Stall.query.get(owner_id)
    
class RoleMixin:
    def has_role(self, roles):
        return self.role in roles

    def get_id(self):
        return '{}:{}'.format(self.role, getattr(self, f'{self.role.lower()}_id'))

class BankAccount(db.Model):
    bank_account_no = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer, nullable = False)

class User(db.Model, RoleMixin, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    bank_account_no = db.Column(db.String(4), db.ForeignKey('bank_account.bank_account_no'), nullable = False)

    user_name = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

    bank_account = db.relationship('BankAccount', backref = db.backref('user', uselist = False))
    food_orders = db.relationship('FoodOrder', backref = 'user')

    role = 'User'

class Stall(db.Model, RoleMixin, UserMixin): #RoleMixin will inherit first, causing UserMixin (2nd child) not be able to override function of 1st child
    stall_id = db.Column(db.Integer, primary_key = True)
    bank_account_no = db.Column(db.String(4), db.ForeignKey('bank_account.bank_account_no'), nullable = False)

    stall_name = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    stall_pic = db.Column(db.String(20), nullable = False, default = 'default.webp')

    menu = db.relationship('Food', backref = 'stall', lazy = True)
    bankaccount = db.relationship('BankAccount', backref = db.backref('stall', uselist = False))
    
    role = 'Stall'

class Food(db.Model):
    food_id = db.Column(db.Integer, primary_key = True)
    stall_id = db.Column(db.Integer, db.ForeignKey('stall.stall_id'), nullable = False)

    food_name = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Numeric(2,2), nullable = False)
    calorie = db.Column(db.Integer, nullable = False)
    preperation_time = db.Column(db.Numeric(2,1), nullable = False)
    description = db.Column(db.String(200), nullable = True)
    food_pic = db.Column(db.String(20), nullable = False, default = 'default.webp')

class FoodOrder(db.Model):
    order_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'), nullable = False)

    status = db.Column(db.String(10), nullable = False)
    time_of_request = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

    time_of_acceptance = db.Column(db.DateTime, nullable = True)
    time_of_ready = db.Column(db.DateTime, nullable = True)
    time_of_fulfilment = db.Column(db.DateTime, nullable = True)

    time_of_failure = db.Column(db.DateTime, nullable = True)
    time_of_withdrawal = db.Column(db.DateTime, nullable = True)