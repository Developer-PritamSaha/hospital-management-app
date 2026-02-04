from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import or_
from datetime import datetime, timedelta

from app_backend_Flask.application.models import *
from ..utils.input_validators import *

class AdminSearchPatientsData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all current patient data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        
        patients = Patient.query.filter(
            or_(
                Patient.full_name.contains(search_str.title()),
                Patient.public_id.ilike(search_str),
                Patient.contact.ilike(search_str),
                Patient.dob.contains(search_str)
            )
        ).all()

        if len(patients) == 0:
            abort(404, message="No Search Result Found.")

        try:
            patient_data = []
            for p in patients:
                t = User.user_email(p.user_id)
                patient_data.append(
                    {
                        'patient_id': p.id,
                        'patient_public_id': p.public_id,
                        'user_id': p.user_id,
                        'full_name': p.full_name,
                        'contact': p.contact,
                        'email': t[0],
                        'is_active': t[1],
                        'dob': p.dob.strftime("%Y-%m-%d"),
                        'gender': p.gender.title(),
                        'height_cm': p.height_cm,
                        'weight_kg': p.weight_kg
                    }
                )

                patient_data.reverse()

            return {
                "count": len(patient_data),
                "patients": patient_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminSearchPatientsData: (triggered) an error: {e}")
            abort(500, message="Patients search data fetching failed.")

class AdminSearchDoctorsData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered  list of all current doctor data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        spec = Specialization.query.filter(Specialization.name.contains(search_str.title())).first()
        if spec == None:
            spec_id = 0
        else:
            spec_id = spec.id
        
        doctors = Doctor.query.filter(
            or_(
                Doctor.full_name.contains(search_str.title()),
                Doctor.public_id.ilike(search_str),
                Doctor.contact.ilike(search_str),
                Doctor.specialization_id == spec_id,
                Doctor.license.ilike(search_str)
            )
        ).all()

        if len(doctors) == 0:
            abort(404, message="No Search Result Found.")

        try:
            doctor_data = []
            for d in doctors:
                t = User.user_email(d.user_id)
                doctor_data.append(
                    {
                        'doctor_id': d.id,
                        'doctor_public_id': d.public_id,
                        'user_id': d.user_id,
                        'full_name': d.full_name,
                        'email': t[0],
                        'is_active': t[1],
                        'department': Departments_Doctors.dept_name(d.id),
                        'specialization': Specialization.spec_name(d.specialization_id),
                        'gender': d.gender.title(),
                        'license': d.license,
                        'experience': d.experience,
                        'description': d.description,
                        'contact': d.contact
                    }
                )

                doctor_data.reverse()

            return {
                "count": len(doctor_data),
                "doctors": doctor_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminSearchDoctorsData: (triggered) an error: {e}")
            abort(500, message="Doctors search data fetching failed.")