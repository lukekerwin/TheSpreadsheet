from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api_credentials import API_URI

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = API_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

engine = create_engine(API_URI)
Session = sessionmaker(bind=engine)
