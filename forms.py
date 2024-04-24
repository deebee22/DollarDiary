from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, DateField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from expense.models import User
import re

class SignUpForm(FlaskForm):
    
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first() #checks if a user with a given username already exists
        if user:
            raise ValidationError('An account for this username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first() #checks if a user with a given email already exists
        if email_address:
            raise ValidationError('An account for this email address already exists! Please try a different email address') 
    
    def contains_special_char(form, field):
        if not re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?\/\\~-]', field.data):
            raise ValidationError('Password must contain at least one special character')
      
    
    username = StringField(label='User Name:', validators=[Length(min=5, max=20), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=10), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired(), contains_special_char])
    submit = SubmitField(label='Create Account')

class SignInForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class ExpenseForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('shopping', 'Shopping'),
        ('home', 'Home'),
        ('school', 'School'),
        ('pet', 'Pet'),
        ('groceries', 'Groceries'),
        ('dining_out', 'Dining Out'),
        ('health_and_wellness', 'Health and Wellness'),
        ('transportation', 'Transportation'),
        ('misc', 'Miscellaneous')
    ], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    submit = SubmitField('Save')