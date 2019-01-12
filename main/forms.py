from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from main.models import Stall, User

class StallRegistrationForm(FlaskForm):
    stall_name = StringField('Stall Name', validators = [DataRequired(), Length(min = 5, max = 20)])
    bank_account_no = StringField('Bank Account Number', validators = [DataRequired(), Length(min = 4, max = 4)])
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 5, max = 20)])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_stall_name(self, stall_name):
        stall = Stall.query.filter_by(stall_name = stall_name.data).first()
        if stall:
            raise ValidationError('This stall name is taken. Please choose another one.')


class StallLoginForm(FlaskForm):
    stall_name = StringField('Stall Name', validators = [DataRequired(), Length(min = 5, max = 20)])
    password = PasswordField('Password', validators = [DataRequired(), Length(min = 5, max = 20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

class UserRegistrationForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    bank_account_no = StringField('Bank Account Number', validators=[DataRequired(), Length(min=4, max=4)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_user_name(self, user_name):
        user = User.query.filter_by(user_name = user_name.data).first()
        if user:
            raise ValidationError('This Username is taken. Please choose another one.')


class UserLoginForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=15)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    

class StallProfileUpdateForm(FlaskForm):
    stall_name = StringField('Stall Name', validators=[DataRequired(), Length(min=5, max=20)])
    bank_account_no = StringField('Bank Account Number', validators=[DataRequired(), Length(min=4, max=4)])
    stall_pic = FileField('Update Stall Picture', validators=[FileAllowed(['png','jpeg','jpg','webp'])])
    submit = SubmitField('Update')

    def validate_stall_name(self, stall_name):
        stall = Stall.query.filter_by(stall_name=stall_name.data).first()
        if stall:
            return ValidationError('This Stall Name is taken. Please choose another one.')
