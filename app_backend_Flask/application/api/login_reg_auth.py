from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_jwt_extended import get_jwt, get_jti
from datetime import datetime, timedelta
import uuid, bcrypt

from ..extensions import db
from app_backend_Flask.application.models.login_model import *
from ..utils.input_validators import *

## Request Parser setup 
# For Patient Data
patientData_validator = reqparse.RequestParser()
patientData_validator.add_argument("full_name", type=non_empty_string, required=True, help="{error_msg}")
patientData_validator.add_argument("email", type=email_validator, required=True, help="{error_msg}")
patientData_validator.add_argument("password", type=validate_passwd, required=True, help="{error_msg}")
patientData_validator.add_argument("dob", type=is_valid_date, required=True, help="{error_msg}")
patientData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
patientData_validator.add_argument("height_cm", type=int, required=True, help="Missing required parameter in the JSON body or not an integer or empty.")
patientData_validator.add_argument("weight_kg", type=int, required=True, help="Missing required parameter in the JSON body or not an integer or empty.")

#For Doctor Data
doctorData_validator = reqparse.RequestParser()
doctorData_validator.add_argument("full_name", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("email", type=email_validator, required=True, help="{error_msg}")
doctorData_validator.add_argument("password", type=validate_passwd, required=True, help="{error_msg}")
doctorData_validator.add_argument("specialization", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("experience", type=int, required=True, help="Missing required parameter in the JSON body or not an integer or empty.")
doctorData_validator.add_argument("description", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("contact", type=int, required=True, help="Missing required parameter in the JSON body or not an integer or empty.")

# For login data
loginData_validator = reqparse.RequestParser()
loginData_validator.add_argument("email", type=email_validator, required=True, help="{error_msg}")
loginData_validator.add_argument("password", type=non_empty_string, required=True, help="{error_msg}")
loginData_validator.add_argument("rememberMe", type=bool, required=True, help="Missing required parameter in the JSON body or not a boolean or empty.")


## Registration API 
class PatientRegistration(Resource):
    '''This resource consist of only 'POST' method which checks rgistration credentials and data sent by the patient's client and register them into the application '''
    def post(self):    
        if not request.is_json:
            return {"error": "Only JSON data allowed"}, 400
        args = patientData_validator.parse_args()

        user_exist = User.query.filter_by(email=args["email"]).first()
        if user_exist:
            abort(409, message="Patient already exist")
        
        ## Check Age and Height and Weight
        dob = args["dob"]
        current_date = datetime.now().date()
        if dob > current_date:
            abort(400, message=" 'dob' can not be in the future.")
        if args["height_cm"] < 55 or args["height_cm"] > 272: # in c.m.
            abort(400, message=" 'height' should be within(55 to 272)cm.")
        if args["weight_kg"] <= 0 or args["weight_kg"] > 350: # in k.g.
            abort(400, message=" 'weight' should be within(1 to 350)kg.")

        try:
            hashed_passwd = bcrypt.hashpw(args["password"].encode("utf-8"), bcrypt.gensalt())

            new_registration = User(
                email = args["email"],
                password = hashed_passwd.decode("utf-8"),
                active = True,
                fs_uniquifier = str(uuid.uuid4())
            )
            db.session.add(new_registration)
            db.session.flush()

            new_patient_data = Patient(
                user_id = new_registration.id,
                full_name = args["full_name"],
                dob = dob,
                gender = args["gender"],
                height_cm = args["height_cm"],
                weight_kg = args["weight_kg"]
            )  
            db.session.add(new_patient_data)
            db.session.flush()

            db.session.add(Roles_Users(user_id=new_registration.id,role_id=3))

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserRegistration: (triggered) new registration commit rollback: (cause) {e}")
            abort(500, message="Registration failed")
        else:
            db.session.commit()
            return {'msg': "Patient Registration Successful"}, 201
        
class DoctorRegistration(Resource):
    '''This resource consist of only 'POST' method which checks rgistration credentials and doctor's data sent by the admin and register them into the application '''
    @jwt_required()
    def post(self):    
        if not request.is_json:
            return {"error": "Only JSON data allowed"}, 400
        
        access_key = get_jwt()
        
        if access_key["role"] != "admin":
            abort(403, message="Admin access needed")
       
        args = doctorData_validator.parse_args()

        user_exist = User.query.filter_by(email=args["email"]).first()
        if user_exist:
            abort(409, message="Doctor already exist")
        if args['experience'] < 0 or args['experience'] > 80:
            abort(400, message=" 'experience' should be within(0 to 80)")
        if len(str(args['contact'])) != 10:
            abort(400, message="Contact must contain 10 digits")
        
        try:
            hashed_passwd = bcrypt.hashpw(args["password"].encode("utf-8"), bcrypt.gensalt())

            new_registration = User(
                email = args["email"],
                password = hashed_passwd.decode("utf-8"),
                active = True,
                fs_uniquifier = str(uuid.uuid4())
            )
            db.session.add(new_registration)
            db.session.flush()

            new_doctor_data = Doctor(
                user_id = new_registration.id,
                full_name = args["full_name"],
                specialization = args["specialization"],
                experience = args["experience"],
                description = args["description"],
                contact = args["contact"]
            )  
            db.session.add(new_doctor_data)
            db.session.flush()

            db.session.add(Roles_Users(user_id=new_registration.id,role_id=2))

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserRegistration: (triggered) new registration commit rollback: (cause) {e}")
            abort(500, message="Registration failed")
        else:
            db.session.commit()
            return {'msg': "Doctor Registration Successful"}, 201
        
## Login API
class UserLogin(Resource):
    '''This resource consist of only 'POST' method which checks login credentials sent by the client and returns the 'access token' and 'refresh token' '''
    def post(self):
        if not request.is_json:
                return {"error": "Only JSON data allowed"}, 400
        args = loginData_validator.parse_args()
        user = User.query.filter_by(email=args["email"]).first()
        
        if not user or not bcrypt.checkpw(args["password"].encode("utf-8"), user.password.encode("utf-8")):
            abort(401, message="Invalid credentials")

        if args["rememberMe"] == True:
            expiry_period = timedelta(days=30)
        else:
            expiry_period = timedelta(days=7)
        
        try:
            prevToken_exist = Refresh_Tokens.query.filter_by(user_id=user.id).first()
            if prevToken_exist:
                # Delete the previuos refresh token
                db.session.delete(prevToken_exist)
       
            jwt_access_token = create_access_token(identity=str(user.id), additional_claims={"role": Roles_Users.user_role(user.id)})
            jwt_refresh_token = create_refresh_token(identity=str(user.id), expires_delta=expiry_period)
            jti_sig = get_jti(jwt_refresh_token)
            new_refresh_token = Refresh_Tokens(
                user_id = user.id,
                jti = jti_sig,
                create_datetime = datetime.now(),
                expiry_datetime = datetime.now() + expiry_period
            )
            db.session.add(new_refresh_token)
            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogin: (triggered) new token commit rollback: (cause) {e}")
            abort(500, message="Login failed")
        else:
            db.session.commit()
            return {
                "msg": "Login Successful",
                "access_token": jwt_access_token,
                "refresh_token": jwt_refresh_token
            }, 200

# Refresh Token validation API
class RefershTokenValidator(Resource):
    '''This resource consist of only 'POST' method which checks 'refresh token' sent by the client and returns the 'access token' '''
    @jwt_required(refresh=True)   
    def post(self):
        refreshToken_payload = get_jwt()
        rfreshToken_jti = refreshToken_payload["jti"]
        user_id = get_jwt_identity()

        refreshToken_exist = Refresh_Tokens.query.filter_by(jti=rfreshToken_jti, user_id=int(user_id)).first()
        
        if not refreshToken_exist or not refreshToken_exist.is_active():
            return {"msg": "Invalid or expired refresh token"}, 401
        prev_token_expiry = refreshToken_exist.expiry_datetime
        expiry_period = (prev_token_expiry - datetime.now())
        try:
            # Delete the previuos refresh access token
            db.session.delete(refreshToken_exist)
            db.session.flush()
        
            # Generate new access and refresh token
            jwt_access_token = create_access_token(identity=user_id, additional_claims={"role": Roles_Users.user_role(int(user_id))})
           
            jwt_refresh_token = create_refresh_token(identity=user_id, expires_delta=expiry_period)
            jti_sig = get_jti(jwt_refresh_token)
           
            new_refresh_token = Refresh_Tokens(
                user_id = int(user_id),
                jti = jti_sig,
                create_datetime = datetime.now(),
                expiry_datetime = prev_token_expiry
            )
            db.session.add(new_refresh_token)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) RefreshTokenValidator: (triggered) new token commit rollback: (cause) {e}")
            abort(500, message="Access Token generation failed")
        else:
            db.session.commit()
            return {
                "access_token": jwt_access_token,
                "refresh_token": jwt_refresh_token
            }, 200
        
# Logout API
class UserLogout(Resource):
    '''This resource consist of only 'POST' method which checks 'access token' sent by the client and revoke the active refresh token  '''
    @jwt_required()   
    def post(self):
        user_id = get_jwt_identity()

        refreshToken_exist = Refresh_Tokens.query.filter_by(user_id=int(user_id)).first()
        
        if not refreshToken_exist or not refreshToken_exist.is_active():
            abort(409, message="Client not logged in.")
       
        try:
            # Delete the previuos refresh token
            db.session.delete(refreshToken_exist)
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogout: (triggered) refresh token delete commit rollback: (cause) {e}")
            abort(500, message="Logout failed")
        else:
            db.session.commit()
            return {"msg": "Logged out successfully"}, 200