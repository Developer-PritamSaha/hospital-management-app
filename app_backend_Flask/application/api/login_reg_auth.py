from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended import get_jwt, get_jti
from datetime import datetime, timedelta
import uuid, bcrypt

from app_backend_Flask.application.db_extensions import db
from app_backend_Flask.application.models import *
from app_backend_Flask.application.utils.input_validators import *
from app_backend_Flask.application.utils.generate_credentials_uid import *

## Request Parser setup 
# For Patient Data
patientData_validator = reqparse.RequestParser()
patientData_validator.add_argument("full_name", type=check_full_name, required=True, help="{error_msg}")
patientData_validator.add_argument("email", type=email_validator, required=True, help="{error_msg}")
patientData_validator.add_argument("password", type=validate_passwd, required=True, help="{error_msg}")
patientData_validator.add_argument("dob", type=is_valid_date, required=True, help="{error_msg}")
patientData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
patientData_validator.add_argument("height_cm", type=is_integer, required=True, help="{error_msg}")
patientData_validator.add_argument("weight_kg", type=is_integer, required=True, help="{error_msg}")
patientData_validator.add_argument("contact", type=is_valid_contact, required=True, help="{error_msg}")

#For Doctor Data
doctorData_validator = reqparse.RequestParser()
doctorData_validator.add_argument("full_name", type=check_full_name, required=True, help="{error_msg}")
doctorData_validator.add_argument("email", type=email_validator, required=True, help="{error_msg}")
doctorData_validator.add_argument("password", type=validate_passwd, required=True, help="{error_msg}")
doctorData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
doctorData_validator.add_argument("license", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("qualification", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("specialization_id", type=is_integer, required=True, help="{error_msg}")
doctorData_validator.add_argument("experience", type=is_integer, required=True, help="{error_msg}")
doctorData_validator.add_argument("department_id", type=is_integer, required=True, help="{error_msg}")
doctorData_validator.add_argument("description", type=non_empty_string, required=True, help="{error_msg}")
doctorData_validator.add_argument("contact", type=is_valid_contact, required=True, help="{error_msg}")

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
            abort(400, message="Only JSON data allowed")
        args = patientData_validator.parse_args()

        user_exist = User.query.filter_by(email=args["email"]).first()
        if user_exist:
            abort(409, message="Patient email already exist")
        
        ## Check Age and Height and Weight
        dob = args["dob"]
        current_date = datetime.now().date()
        if dob > current_date:
            abort(400, message={
                'dob': "DOB can not be in the future."
            })
        if current_date.year - dob.year > 100:
            abort(400, message={
                'dob': "Age can not be greater than 100."
            })
        
        if args["height_cm"] < 55 or args["height_cm"] > 272: # in c.m.
            abort(400, message={
                'height_cm': "Height should be within (55 to 272) cm."
            })
        if args["weight_kg"] <= 0 or args["weight_kg"] > 350: # in k.g.
            abort(400, message={
                'weight_kg': "Weight should be within (1 to 350) kg."
            })

        try:
            hashed_passwd = bcrypt.hashpw(args["password"].encode("utf-8"), bcrypt.gensalt())

            new_registration = User(
                email = args["email"],
                password = hashed_passwd.decode("utf-8"),
                is_active = True,
                fs_uniquifier = str(uuid.uuid4())
            )
            db.session.add(new_registration)
            db.session.flush()

            new_patient_data = Patient(
                user_id = new_registration.id,
                public_id = generate_uuid("PA",6),
                full_name = args["full_name"].title(),
                contact = args["contact"],
                dob = dob,
                gender = args["gender"],
                height_cm = args["height_cm"],
                weight_kg = args["weight_kg"]
            )  
            db.session.add(new_patient_data)
            db.session.flush()

            db.session.add(Roles_Users(user_id=new_registration.id,role_id=3))

            app.extensions["cache_data"].delete("patient_cache")

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) PatientRegistration: (triggered) new registration commit rollback: (cause) {e}")
            abort(500, message="Patient Registration failed")
        else:
            db.session.commit()
            return {'message': "Patient Registration Successful"}, 201
        
class DoctorRegistration(Resource):
    '''This resource consist of only 'POST' method which checks rgistration credentials and doctor's data sent by the admin and register them into the application '''
    @jwt_required()
    def post(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(403, message="Admin access needed")
       
        args = doctorData_validator.parse_args()

        user_exist = User.query.filter_by(email=args["email"]).first()
        if user_exist:
            abort(409, message="Doctor email already exist")
        if args['experience'] < 1 or args['experience'] > 80:
            abort(400, message={
                'experience': "Experience should be within(1 to 80)"
            })
        if not Department.query.filter_by(id=args["department_id"]).first():
            abort(404, message={
                'department_id': "Department id donot exist"
            })
        if not Specialization.query.filter_by(id=args["specialization_id"]).first():
            abort(404, message={
                'specialization_id': "Specialization id donot exist"
            })
        if Doctor.query.filter_by(license=args["license"]).first():
            abort(400, message={
                'license': "License provided already exist"
            })
        
        try:
            hashed_passwd = bcrypt.hashpw(args["password"].encode("utf-8"), bcrypt.gensalt())

            new_registration = User(
                email = args["email"],
                password = hashed_passwd.decode("utf-8"),
                is_active = True,
                fs_uniquifier = str(uuid.uuid4())
            )
            db.session.add(new_registration)
            db.session.flush()

            doc_public_id = generate_uuid("DR",6)
            new_doctor_data = Doctor(
                user_id = new_registration.id,
                public_id = doc_public_id,
                specialization_id = args["specialization_id"],
                full_name = args["full_name"].title(),
                gender = args["gender"],
                license = args["license"],
                qualification = args["qualification"].upper(),
                experience = args["experience"],
                description = args["description"],
                contact = args["contact"]
            )  
            db.session.add(new_doctor_data)
            db.session.flush()

            db.session.add(Roles_Users(user_id=new_registration.id,role_id=2))
            db.session.flush()

            db.session.add(Departments_Doctors(doctor_id=new_doctor_data.id, department_id=args["department_id"]))
            db.session.flush()

            Availability.create_default_availability(new_doctor_data.id)
            
            save_credentials(args["email"],args["password"],f'./doctor_credentials/{doc_public_id}_cred.txt',f'[ {args["full_name"].title().replace(" ","_")} ({doc_public_id}) ] doctor')

            app.extensions["cache_data"].delete("doctor_cache")
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorRegistration: (triggered) new registration commit rollback: (cause) {e}")
            abort(500, message="Doctor Registration failed")
        else:
            db.session.commit()
            return {'message': "Doctor Registration Successful"}, 201
        
## Login API
class UserLogin(Resource):
    '''This resource consist of only 'POST' method which checks login credentials sent by the client and returns the 'access token' and 'refresh token' '''
    def post(self):
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        args = loginData_validator.parse_args()
        user = User.query.filter_by(email=args["email"]).first()
        
        if user != None: 
            if not user.is_active:
                abort(401, message="User has been blacklisted")
            if not bcrypt.checkpw(args["password"].encode("utf-8"), user.password.encode("utf-8")):
                abort(401, message="Invalid credential")
        else:
            abort(404, message="User do not exist")

        if args["rememberMe"] == True:
            expiry_period = timedelta(days=30)
        else:
            expiry_period = timedelta(days=7)
        
        try:
            jwt_refresh_token = create_refresh_token(identity=str(user.id), expires_delta=expiry_period)
            refresh_jti_sig = get_jti(jwt_refresh_token)
            jwt_access_token = create_access_token(identity=str(user.id), additional_claims={"role": Roles_Users.user_role(user.id), "refresh_jti": refresh_jti_sig})
            access_jti_sig = get_jti(jwt_access_token)
            
            new_refresh_token = User_Tokens(
                user_id = user.id,
                jti = refresh_jti_sig,
                parent_jti = "NA",
                type = "refresh",
                create_datetime = datetime.now(),
                expiry_datetime = datetime.now() + expiry_period
            )
            new_access_token = User_Tokens(
                user_id = user.id,
                jti = access_jti_sig,
                parent_jti = refresh_jti_sig,
                type = "access",
                create_datetime = datetime.now(),
                expiry_datetime = datetime.now() + timedelta(minutes=10)
            )

            db.session.add(new_refresh_token)
            db.session.add(new_access_token)
            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogin: (triggered) new token commit rollback: (cause) {e}")
            abort(500, message="Login failed")
        else:
            db.session.commit()
            return {
                "access_token": jwt_access_token,
                "refresh_token": jwt_refresh_token
            }, 200

# Access Token refresh API
class TokenRefresher(Resource):
    '''This resource consist of only 'GET' method which checks 'refresh token' sent by the client and returns the 'access token' '''
    @jwt_required(refresh=True)   
    def post(self):
        refreshToken_payload = get_jwt()
        rfreshToken_jti = refreshToken_payload["jti"]
        userId = get_jwt_identity()

        user = User.query.filter_by(id=int(userId)).first()
        if not user.is_active:
            abort(401, message="User has been blacklisted")

        refreshToken_exist = User_Tokens.query.filter_by(jti=rfreshToken_jti).first()
        
        if not refreshToken_exist or not refreshToken_exist.is_valid():
            abort(401, message="Invalid or expired refresh token")
        
        try:
            # Invalidate Previous access token
            prev_accessToken = User_Tokens.query.filter_by(user_id=int(userId), type='access', valid=True, parent_jti=rfreshToken_jti).first()

            prev_accessToken.valid = False
            db.session.flush()

            # Generate new access token
            jwt_access_token = create_access_token(identity=str(userId), additional_claims={"role": Roles_Users.user_role(int(userId)), "refresh_jti": rfreshToken_jti})
        
            jti_sig = get_jti(jwt_access_token)
           
            new_access_token = User_Tokens(
                user_id = int(userId),
                jti = jti_sig,
                parent_jti = rfreshToken_jti,
                type = "access",
                create_datetime = datetime.now(),
                expiry_datetime = datetime.now() + timedelta(minutes=10)
            )
            db.session.add(new_access_token)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) TokenRefresher: (triggered) new token commit rollback: (cause) {e}")
            abort(500, message="Access Token generation failed")
        else:
            db.session.commit()
            return {
                "access_token": jwt_access_token
            }, 200
        
class UserTokenRole(Resource):
    '''This resource consist of only 'POST' method which checks 'refresh token' for the client is still valid or not and returns the user role'''
    @jwt_required()   
    def get(self):
        accessToken_payload = get_jwt()
        rfreshToken_jti = accessToken_payload["refresh_jti"]
        user_id = get_jwt_identity()

        user = User.query.filter_by(id=int(user_id)).first()
        if not user.is_active:
            abort(401, message={'status': "revoked"})

        refreshToken_exist = User_Tokens.query.filter_by(jti=rfreshToken_jti).first()

        if not refreshToken_exist or not refreshToken_exist.is_valid():
            abort(401, message={'status': "invalid"})
        else:
            return {
                "status": "valid",
                "role": Roles_Users.user_role(int(user_id))
            }, 200
        
# Logout API
class UserLogout(Resource):
    '''This resource consist of only 'POST' method which checks 'access token' sent by the client and revoke the active refresh token  '''
    @jwt_required()   
    def post(self):
        accessToken_payload = get_jwt()
        accessToken_jti = accessToken_payload["jti"]
        rfreshToken_jti = accessToken_payload["refresh_jti"]

        refreshToken_exist = User_Tokens.query.filter_by(jti=rfreshToken_jti).first()
        accessToken_exist = User_Tokens.query.filter_by(jti=accessToken_jti).first()

        if not accessToken_exist or not refreshToken_exist or not refreshToken_exist.is_valid():
            abort(401, message="Logout failed: User not logged in.")
       
        try:
            accessToken_exist.valid = False
            refreshToken_exist.valid = False
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogout: (triggered) token invalidation commit rollback: (cause) {e}")
            abort(500, message="Logout failed")
        else:
            db.session.commit()
            return {"message": "Logged out successfully"}, 200
        
# Logout Everywhere API
class UserLogoutEverywhere(Resource):
    '''This resource consist of only 'POST' method which checks 'access token' sent by the client and revoke all the active refresh and access token'''
    @jwt_required()   
    def post(self):
        accessToken_payload = get_jwt()
        accessToken_jti = accessToken_payload["jti"]
        rfreshToken_jti = accessToken_payload["refresh_jti"]
        user_id = get_jwt_identity()

        refreshToken_exist = User_Tokens.query.filter_by(jti=rfreshToken_jti).first()
        accessToken_exist = User_Tokens.query.filter_by(jti=accessToken_jti).first()

        if not user_id or not accessToken_exist or not refreshToken_exist or not refreshToken_exist.is_valid():
            abort(401, message="Logout failed: User not logged in.")
       
        try:
            tokens = User_Tokens.query.filter_by(user_id=int(user_id), valid=True).all()
            for t in tokens:
                t.valid = False
                db.session.flush()
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogoutEverywhere: (triggered) token invalidation commit rollback: (cause) {e}")
            abort(500, message="Logout failed")
        else:
            db.session.commit()
            return {"message": "Logged out everywhere successfully"}, 200