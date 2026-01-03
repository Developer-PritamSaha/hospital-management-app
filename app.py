import os, sys
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app_backend_Flask.application.app_config import LocalDevConfig
from app_backend_Flask.application.extensions import db
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format=f'%(asctime)s - %(levelname)s - %(name)s : %(message)s')

app = None

def create_app():
    app = Flask(__name__, static_folder="dist_frontend_VUE", static_url_path="")
    if os.getenv('ENV', "development") == "production":
      raise Exception("\n>> Currently no production config is setup.")
    else:
      print("\n>> Staring Local Development...")
      app.config.from_object(LocalDevConfig)

    # Initialize extensions
    db.init_app(app)

    app.app_context().push()
    return app

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}) # For dev uses (not recommended, this will expose your api endpoints to any domains)
# CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
api = Api(app)
jwt = JWTManager(app)

@jwt.unauthorized_loader
def missing_token_callback(e):
    return {
        "error": "Authorization required",
        "message": "Missing bearer authorization token in the header."
    }, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {
        "error": "Token Expired",
        'message': 'The authorization token has expired.'
    }, 403

## Imports all the API resources so they are loaded 
from app_backend_Flask.application.api.login_reg_auth import *

## Imports all the Models so they are loaded 
from app_backend_Flask.application.models import *

# Import the Vue frontend to serve
from app_backend_Flask.application.index import *

## Adding APi resorces to their respective routes
api.add_resource(PatientRegistration, "/api/register")
api.add_resource(DoctorRegistration, "/api/register/doctor")
api.add_resource(UserLogin, "/api/login")
api.add_resource(RefershTokenValidator, "/api/refresh")
api.add_resource(UserLogout, "/api/logout")


if __name__ == '__main__':
  db_init_success = False
  ## Create the database tables or schema if they do not exist
  try:
    with app.app_context():
        db.create_all()
    print(">> Database Initialized successfully..")

    # Initialize default roles and admin user if not already initialized
    Role.create_default_roles()
    if not Roles_Users.query.filter_by(user_id=1, role_id=1).first():
        print("\n<!> No admin account found. Intializing with new admin credentials.")
        User.create_admin()

    db_init_success = True

  except Exception as e:
    db.session.rollback()
    app.logger.exception(f"App Initialization failed: (cause) {e}")
    print("*>> App Initialization failed..")


  if(db_init_success):
    # Run the Flask app
    port = 5080
    print(f"\n🚀 Hospital Management App is running at: http://127.0.0.1:{port}/\n   (ctrl + c - to quit)\n")
    app.run(host='0.0.0.0',port=port)
  else:
    print("\n<!> Exiting the app...")
    sys.exit(1)

