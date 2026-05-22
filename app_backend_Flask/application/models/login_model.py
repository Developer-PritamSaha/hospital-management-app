from flask import current_app as app
from datetime import datetime
import bcrypt, uuid
from app_backend_Flask.application.db_extensions import db
from app_backend_Flask.application.utils.generate_credentials_uid import *

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    fs_uniquifier = db.Column(db.String(50), unique=True, nullable=False)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    patient = db.relationship('Patient', backref='user', cascade="all, delete-orphan")
    doctor = db.relationship('Doctor', backref='user', cascade="all, delete-orphan")
    user_token = db.relationship('User_Tokens', backref='user', cascade="all, delete-orphan")
    notification = db.relationship('Notification', backref='user', cascade="all, delete-orphan")

    @classmethod
    def create_admin(cls):
        '''Creates an admin account into the database programatically else raises Exception'''
        while True:
            try:          
                email = generate_id()
                passwd = generate_password()
                hashed_passwd = bcrypt.hashpw(passwd.encode("utf-8"), bcrypt.gensalt())
                break
            except ValueError as e:
                print(f"\n  <!> {e} Please try again.")
            except Exception as e:
                print(f"\n  <!> Unexpected error: {e} Try again.")
   
        try:
            new_registration = User(
                email = email,
                password = hashed_passwd.decode("utf-8"),
                is_active = True,
                fs_uniquifier = str(uuid.uuid4())
            )
            db.session.add(new_registration)
            db.session.flush()

            db.session.add(Roles_Users(user_id=new_registration.id,role_id=1))

            print(f"\n Admin User ID: {email}")
            print(f"\n Admin Password: {passwd}")
            # if(input("\n#> Do you want to save a copy of the credential(y/n): ") != 'n'):
            save_credentials(email,passwd,"./admin_credential.txt","Default Admin")
            print("\n>> Admin Credentials Initialized Successfully...\n**Please keep a note of the provided credentials**\n")
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) User.create_admin(): (triggered) admin commit rollback: (cause) {e}")
            raise Exception(e)
        else:
            db.session.commit()

    @classmethod
    def user_email(cls, userId: int):
        '''Returns a tuple ('email','is_active') for the respective user-id if exist else return "None"'''
        try:
            user = User.query.filter_by(id=int(userId)).first()
        except Exception as e:
            app.logger.exception(f"(Method) Role.user_role(): (cause) {e}")
            return(None)
        else:
            return (user.email, user.is_active)
        
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    @classmethod
    def create_default_roles(cls):
        '''Creates default roles ['admin','doctor','patient'] into the database else raises Exception'''
        try:
            existing_roles = {role.name for role in Role.query.all()}

            if ("admin" not in existing_roles) or ("patient" not in existing_roles) or ("doctor" not in existing_roles):
                new_role = Role(
                    name = "admin",
                    description = '''
                        * Admin is the pre-existing superuser of the application
                        * Can add, update, and delete doctor profiles (name, specialization, availability).
                        * Can view and manage all appointments.
                        * Can search for patients or doctors by name/specialization.
                    '''
                )
                db.session.add(new_role)
                db.session.flush()

                new_role = Role(
                    name = "doctor",
                    description = '''
                       * Can log in to view assigned appointments.
                       * Can mark a patient's visit as completed and enter diagnosis & treatment notes.
                       * Can view and update patient history (previous diagnoses & prescriptions).
                    '''
                )
                db.session.add(new_role)
                db.session.flush()

                new_role = Role(
                    name = "patient",
                    description = '''
                        * Can register, log in, and update their profile.
                        * Can search for doctors by specialization and availability.
                        * Can book, reschedule, or cancel an appointment.
                        * Can view their own appointment history and treatment details.
                    '''
                )
                db.session.add(new_role)
                db.session.flush()
            else:
                return None

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) Role.create_default_role(): (triggered) default roles commit rollback: (cause) {e}")
            raise Exception(e)
        else:
            db.session.commit()
        
class Roles_Users(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)  

    @classmethod
    def user_role(cls, userId: int):
        '''Returns the role_name of the user if exist else return "None"'''
        try:
            role_id = Roles_Users.query.filter_by(user_id=int(userId)).first().role_id
            role_name = Role.query.filter_by(id=role_id).first().name
        except AttributeError:
            return(None)
        except Exception as e:
            app.logger.exception(f"(Method) Roles_Users.user_role(): (cause) {e}")
            return(None)
        else:
            return str(role_name)

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)  
    public_id = db.Column(db.String(10), nullable=False, unique=True, index=True)
    full_name = db.Column(db.String(100), nullable=False, index=True)
    contact = db.Column(db.String(20), nullable=False, index=True)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    height_cm = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Integer, nullable=False)
    patient_appointment = db.relationship('Appointment', backref='patient', cascade="all, delete-orphan")

class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)  
    specialization_id = db.Column(db.Integer, db.ForeignKey("specialization.id"), nullable=False, index=True)
    public_id = db.Column(db.String(10), nullable=False, unique=True, index=True) 
    full_name = db.Column(db.String(100), nullable=False, index=True)
    gender = db.Column(db.String(20), nullable=False)
    license = db.Column(db.String(40), nullable=False, unique=True, index=True)
    qualification = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(40), nullable=False, index=True)
    doc_department = db.relationship('Department', secondary='departments_doctors', backref=db.backref('doctors', lazy='dynamic'))
    doc_availability = db.relationship('Availability', backref='doctor', cascade="all, delete-orphan")
    doctor_appointment = db.relationship('Appointment', backref='doctor', cascade="all, delete-orphan")
    
class User_Tokens(db.Model):
    __tablename__ = "user_tokens"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    jti = db.Column(db.String(255), nullable=False, unique=True, index=True)
    parent_jti = db.Column(db.String(255), nullable=False, unique=False, index=True)
    type = db.Column(db.String(20), nullable=False)
    create_datetime = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    expiry_datetime = db.Column(db.DateTime, nullable=False)
    valid = db.Column(db.Boolean, default=True, nullable=False)

    def is_valid(self):
        """Return True if the token is valid and not expired else False"""
        return (self.valid and datetime.now() < self.expiry_datetime)