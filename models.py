from expense import app, db, login_manager
from flask_login import UserMixin
from datetime import datetime
from expense import bcrypt



@login_manager.user_loader #reload the user object from the user ID stored in the session
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=20), unique=True, nullable=False)
    email_address = db.Column(db.String(length=50), unique=True, nullable=False)
    hash_password = db.Column(db.String(length=60), nullable=False)
    expenses = db.Relationship('Expenses', backref='owned_user', lazy=True) #backref allows us to see the user that certain expenses belong to
    budgets = db.Relationship('Budgets', backref='owned_user', lazy=True)

    @property #additional attribute accessible from each instance of user
    def password(self):
        return self.password #return field when user/developer wants it 
    
    @password.setter #following lines will be executed before password is set to a user instance
    def password(self, plain_text_password): #takes password entered by user into form
        self.hash_password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.hash_password, attempted_password)
    


class Expenses(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=False, unique=False)
    amount = db.Column(db.Float(), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    owner = db.Column(db.Integer(),db.ForeignKey('user.id'))


    def __repr__(self): #return string instead of object location in cmd prompt
        return f'Expense {self.description}'
    

class Budgets(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    amount = db.Column(db.Float)
    time = db.Column(db.String(10))
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer(),db.ForeignKey('user.id'))
    

    
with app.app_context():
    db.create_all()
