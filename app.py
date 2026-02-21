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
    app = Flask(__name__, static_folder="./app_frontend_VUE/dist", static_url_path="")
    if os.getenv('ENV', "development") == "production":
      raise Exception("\n>> Currently no production config is setup.")
    else:
      print("\n<#> Welcome to Hospital Management System \n")
      print(">> Staring Local Development...")
      app.config.from_object(LocalDevConfig)

    # Initialize extensions
    db.init_app(app)

    app.app_context().push()
    return app

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}) ## For dev uses (not recommended, this will expose the api endpoints to any domains)

api = Api(app)
jwt = JWTManager(app)

## Imports all the Models so they are loaded 
from app_backend_Flask.application.models import *

# JWT error handler
@jwt.unauthorized_loader
def missing_token_callback(e):
    return {
        "error": "Authorization required",
        "message": "Missing bearer authorization token in the header."
    }, 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    token_type = jwt_payload["type"]
    return {
        "error": "Token Expired",
        'message': f"The authorization {token_type} token has been expired."
    }, 403

@jwt.invalid_token_loader
def invalid_token_callback(e):
   return {
        "error": "Invalid Token",
        'message': f"The authorization token has: {e}."
   }, 422

@jwt.token_in_blocklist_loader
def check_token_validility(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = User_Tokens.query.filter_by(jti=jti).first()
    if (token == None) or not token.is_valid():
       return True
    else:
       return False

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
   token_type = jwt_payload["type"]
   return{
      "error": "Token Revoked",
      "message": f"The authorization {token_type} token has been revoked.",
   }, 401

## Imports all the API resources so they are loaded 
from app_backend_Flask.application.api import *

# Import the Vue frontend to serve
from app_backend_Flask.application.index import *

### Adding API resorces to their respective routes
## Login Registration APIs
api.add_resource(PatientRegistration, "/api/register/patient")
api.add_resource(DoctorRegistration, "/api/register/doctor")
api.add_resource(UserLogin, "/api/login")
api.add_resource(TokenRefresher, "/api/token/refresh")
api.add_resource(UserTokenRole, "/api/token/user/role-valid")
api.add_resource(UserLogout, "/api/logout")
api.add_resource(UserLogoutEverywhere, "/api/logout/all")

## Search APIs
api.add_resource(AdminSearchPatientsData, "/api/dashboard/admin/patients/search")
api.add_resource(AdminSearchDoctorsData, "/api/dashboard/admin/doctors/search")
api.add_resource(DoctorSearchAssignedPatientsData, "/api/dashboard/doctor/assigned-patients/search")
api.add_resource(DoctorSearchUpcomingAppointments, "/api/dashboard/doctor/appointments/search")

## Admin APIs
api.add_resource(AdminDashboard, "/api/dashboard/admin")
api.add_resource(AdminPatientsData, "/api/dashboard/admin/patients")
api.add_resource(AdminDoctorsData, "/api/dashboard/admin/doctors")
api.add_resource(StatsCount, "/api/dashboard/admin/stats")
api.add_resource(DepartmentList, "/api/dashboard/admin/departments")
api.add_resource(SpecializationList, "/api/dashboard/admin/specializations")
api.add_resource(AdminManageDoctor, "/api/dashboard/admin/doctor")
api.add_resource(AdminManagePatient, "/api/dashboard/admin/patient")

## Doctor APIs
api.add_resource(DoctorDashboard, "/api/dashboard/doctor")
api.add_resource(DocStatsCount, "/api/dashboard/doctor/week-stats")
api.add_resource(DoctorManageAvailability, "/api/dashboard/doctor/availability")
api.add_resource(DoctorManageAppointments, "/api/dashboard/doctor/appointments")
api.add_resource(DoctorAssignedPatient, "/api/dashboard/doctor/assigned-patients")
api.add_resource(DoctorPatientTreatmentHistory, "/api/dashboard/doctor/patient-history")
api.add_resource(PatientAppointmentTreatmentData, "/api/dashboard/doctor/treatment-data")

## Patient APIs
api.add_resource(PatientDashboard, "/api/dashboard/patient")
api.add_resource(PatientAvailableDoctors, "/api/dashboard/patient/doctor-list")
api.add_resource(PatientBookAppointment, "/api/dashboard/patient/book-appointment")

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

    # Build frontend distribution
    build_frontend_dist(rebuild=False) ## rebuild=False

    init_success = True

  except Exception as e:
    db.session.rollback()
    app.logger.exception(f"App Initialization failed: (cause) {e}")
    print("*>> App Initialization failed..")


  if(init_success):
    # Run the Flask app
    port = 5080
    print(f"\n@>> Hospital Management App is running at: http://127.0.0.1:{port}/\n   (ctrl + c - to quit)\n")
    app.run(host='0.0.0.0',port=port)
  else:
    print("\n<!> Exiting the app...")
    sys.exit(1)

