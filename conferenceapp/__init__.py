from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from flask_migrate import Migrate


app = Flask(__name__, instance_relative_config=True)
csrf = CSRFProtect(app)


from conferenceapp import config
app.config.from_object(config.ProductionConfig)
app.config.from_pyfile('config.py', silent=False)
mail = Mail(app) #this should always be after loading config 

db = SQLAlchemy(app)

migrate=Migrate(app,db)

from conferenceapp.myroutes import adminroutes, userroutes
from conferenceapp import forms, mymodels