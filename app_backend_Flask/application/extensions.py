from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
# from flask_restful import Api
# from flask_jwt_extended import JWTManager

engine = None
Base = declarative_base()
db = SQLAlchemy()
# jwt = JWTManager()
# api = Api()