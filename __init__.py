from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db' #allows flask app to recognize the db
app.config['SECRET_KEY'] = '07ed914727f0bf228c2722d5'
db = SQLAlchemy(app) #passing our app into the db
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "signin_page"
login_manager.login_message_category = "info"
from expense import routes
