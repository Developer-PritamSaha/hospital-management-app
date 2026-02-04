from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import marshal_with, abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from ..extensions import db
from app_backend_Flask.application.models import *


# Dashboard handler API
class UserDashboard(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with general user data'''
    @jwt_required()   
    def get(self):
        try:
            user_id = get_jwt_identity()
            user_role = Roles_Users.user_role(int(user_id))
            user = User.query.filter_by(id=int(user_id)).first()
            if user and user_role in ["admin", "doctor", "patient"]:
                if user_role == "admin":
                    return {
                        "email": user.email,
                        "role": user_role.lower(),
                        "name": 'PentaFlow Admin'
                    }, 200
                elif user_role == "patient":
                    patient_data = Patient.query.filter_by(user_id=int(user_id)).first()
                    return {
                        "email": user.email,
                        "role": user_role.lower(),
                        "name": patient_data.full_name,
                        "dob": patient_data.dob.strftime("%Y-%m-%d"),
                        "gender": patient_data.gender,
                        "height_cm": patient_data.height_cm,
                        "weight_kg": patient_data.weight_kg
                    }, 200
                else:
                    doctor_data = Doctor.query.filter_by(user_id=int(user_id)).first()
                    return {
                        "email": user.email,
                        "role": user_role.lower(),
                        "name": doctor_data.full_name,
                        "specialization": doctor_data.specialization,
                        "experience": doctor_data.experience,
                        "description": doctor_data.description,
                        "contact": doctor_data.contact
                    }, 200
            else:
                abort(401, message="Dashboard Access denied.")
        except Exception as e:
            app.logger.exception(f"(Resource) Dashboard: (triggered) an error: {e}")
            abort(500, message="User data fetching failed.")

