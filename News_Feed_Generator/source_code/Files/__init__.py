import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager
#from .models import User


app = Flask(__name__,static_url_path='/static')

app.config['SECRET_KEY'] = 'ajsbcjajh12g7675&%&^@%&#@^(@HVGVGKFDSI^&%^@%(%^#@^T(@^^%^#$'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

Migrate(app,db)
login_manager = LoginManager()
login_manager.login_view = 'http://localhost:5000/login'
login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#     # since the user_id is just the primary key of our user table, use it in the query for the user
#     return User.query.get(int(user_id))


from .main import news
app.register_blueprint(news,url_prefix='/')
