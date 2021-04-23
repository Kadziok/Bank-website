from flask import Flask
#from app import config.Config
from app.config import Config
from app import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

# Dane do maila do wysyłania wiadamości
# przy resecie hasła
"""
app.config['MAIL_SERVER']='smtp.provider.pl'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mail@example.com'
app.config['MAIL_PASSWORD'] = 'pass'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
"""
mail = Mail(app)

from app import routes, models