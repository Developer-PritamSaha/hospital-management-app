import os, sys
from flask import Flask
from flask_mail import Mail
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app_backend_Flask.application.app_config import LocalDevConfig
from app_backend_Flask.application.extensions import db
from app_backend_Flask.application.make_celery import init_celery_app
from app_backend_Flask.application.subprocess_starter import *
import logging

logging.basicConfig(filename='./logs/app.log', level=logging.DEBUG, format=f'%(asctime)s - %(levelname)s - %(name)s : %(message)s')

app = None
celery = None

def create_app():
    app = Flask(__name__, template_folder="./app_backend_Flask/application/templates", static_folder="./app_frontend_VUE/dist", static_url_path="")
    if os.getenv('ENV', "development") == "production":
      raise Exception("\n>> Currently no production config is setup.")
    else:
      print("\n<#> Welcome to Hospital Management System \n")
      print(">> Staring Local Development...")
      app.config.from_object(LocalDevConfig)

    # Initialize extensions
    db.init_app(app)
    api = Api(app)
    mail = Mail(app)
    jwt = JWTManager(app)
    app.app_context().push()

    celery = init_celery_app(app)

    app.extensions["api"] = api
    app.extensions["jwt"] = jwt
    app.extensions["mail"] = mail

    return app, celery


app, celery = create_app()

CORS(app, resources={r"/api/*": {"origins": "*"}}) ## For dev uses (not recommended, this will expose the api endpoints to any domains)


## Imports all the database models
from app_backend_Flask.application.models import *

## Imports all the app routes and jwt error handler
from app_backend_Flask.application.controllers import *


if __name__ == '__main__':
  init_success = False
  ## Create the database tables or schema
  try:
    with app.app_context():
        db.create_all()
    print(">> Database Initialized successfully...")

    # Initialize default roles and admin user 
    Role.create_default_roles()
    if not Roles_Users.query.filter_by(user_id=1, role_id=1).first():
        print("\n<!> No admin account found. Intializing with new admin credentials.")
        User.create_admin()

    # Initialize default departments and specializations
    Department.create_default_departments()
    Specialization.create_default_specializations()

    # Start celery services
    start_celery_workers_beats()

    # Build frontend distribution
    build_frontend_dist()

    init_success = True

  except Exception as e:
    db.session.rollback()
    app.logger.exception(f"App Initialization failed: (cause) {e}")
    print("[!] App Initialization failed..")


  if(init_success):
    # Run the Flask app
    port = 5080
    print(f"\n@>> Hospital Management App is running at: http://127.0.0.1:{port}/\n   (ctrl + c - to quit)\n")
    app.run(host='0.0.0.0',port=port)
  else:
    print("\n<!> Exiting the app...")
    sys.exit(1)

