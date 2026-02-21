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

class DoctorSearchAssignedPatientsData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all current assigned patient data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
             abort(404, message="Doctor not found.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        
        searched_patients = Patient.query.filter(
            or_(
                Patient.full_name.contains(search_str.title()),
                Patient.public_id.ilike(search_str)
                # Patient.gender.ilike(search_str.lower())
            )
        ).all()

        if len(searched_patients) == 0:
            abort(404, message="No Search Result Found.")

        searched_patients_id = [p.id for p in searched_patients]

        # Current weeks appointments
        appointments = []

        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
        for i in range(0,7):
            ap_date = current_week_start_date + timedelta(days=i)
            ap = Appointment.query.filter_by(doctor_id=doctor.id, date=ap_date, status='booked').all()
            appointments += ap

        try:
            assigned_patients = []
            for ap in appointments:
                if ap.patient_id in searched_patients_id:
                    patient = Patient.query.filter_by(id=ap.patient_id).first()
                    if not patient:
                        return{
                            'message': "Patient not exist."
                        }, 404
                    else:
                        patient_age = datetime.now().year - patient.dob.year

                        assigned_patients.append(
                            {
                                'appointment_public_id': ap.public_id,
                                'patient_public_id': patient.public_id,
                                'patient_full_name': patient.full_name,
                                'patient_gender': patient.gender.title(),
                                'patient_age': patient_age,
                                'patient_height': patient.height_cm,
                                'patient_weight': patient.weight_kg,
                                'date': ap.date.strftime("%Y-%m-%d"),
                                'start_time': ap.start_time.strftime("%H:%M"),
                                'end_time': ap.end_time.strftime("%H:%M")
                            }
                        )

            return {
                "count": len(assigned_patients),
                "week_start_date": current_week_start_date.strftime("%Y-%m-%d"),
                "week_end_date": (current_week_start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                "assigned_patients": assigned_patients
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) DoctorSearchAssignedPatientsData: (triggered) an error: {e}")
            abort(500, message="Patients search data fetching failed.")

class DoctorSearchUpcomingAppointments(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all upcoming appointments'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
             abort(404, message="Doctor not found.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")


        searched_appointments = Appointment.query.filter(
            or_(
                Appointment.date.contains(search_str),
                Appointment.public_id.ilike(search_str),
                Appointment.start_time.contains(search_str)
            )
        ).all()

        if len(searched_appointments) == 0:
            abort(404, message="No Search Result Found.")

        # Current weeks appointments
        appointments = []

        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
        for i in range(0,7):
            ap_date = current_week_start_date + timedelta(days=i)
            ap = Appointment.query.filter_by(doctor_id=doctor.id, date=ap_date, status='booked').all()
            appointments += ap

        try:
            appointments_data = []
            for ap in appointments:
                if ap in searched_appointments:
                    patient = Patient.query.filter_by(id=ap.patient_id).first()
                    if not patient:
                        return{
                            'message': "Patient not exist."
                        }, 404
                    else:
                        pat_age = current_datetime.year - patient.dob.year

                        appointments_data.append(
                            {
                                'appointment_public_id': ap.public_id,
                                'patient_public_id': patient.public_id,
                                'patient_full_name': patient.full_name,
                                'patient_gender': patient.gender.title(),
                                'patient_age': pat_age,
                                'patient_height': patient.height_cm,
                                'patient_weight': patient.weight_kg,
                                'date': ap.date.strftime("%Y-%m-%d"),
                                'start_time': ap.start_time.strftime("%H:%M"),
                                'end_time': ap.end_time.strftime("%H:%M"),
                                'status': ap.status,
                                'is_treatment_exist': Treatment.query.filter_by(appointment_id=ap.id).first() is not None
                            }
                        )

            if len(appointments_data) == 0:
                return{ "message":"No Search Result Found."}, 404
            else:
                return {
                    "count": len(appointments_data),
                    "week_start_date": current_week_start_date.strftime("%Y-%m-%d"),
                    "week_end_date": (current_week_start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                    "appointments": appointments_data
                }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) DoctorSearchUpcomingAppointments: (triggered) an error: {e}")
            abort(500, message="Upcoming Appointments search data fetching failed.")