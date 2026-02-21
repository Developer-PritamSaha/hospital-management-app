from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from ..extensions import db
from app_backend_Flask.application.models import *
from ..utils.input_validators import *

## For Patient Appointments Data
patientAppointmentsData_validator = reqparse.RequestParser()
patientAppointmentsData_validator.add_argument("doctor_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientAppointmentsData_validator.add_argument("slot_id", type=non_empty_string, required=True, help="{error_msg}")
patientAppointmentsData_validator.add_argument("slot_date", type=is_valid_date, required=True, help="{error_msg}")
patientAppointmentsData_validator.add_argument("slot_start_time", type=is_valid_time, required=True, help="{error_msg}")
patientAppointmentsData_validator.add_argument("slot_end_time", type=is_valid_time, required=True, help="{error_msg}")

# Patient Dashboard handler API
class PatientDashboard(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with respective patient data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        user_exist = User.query.filter_by(id=int(user_id)).first()
        patient = Patient.query.filter_by(user_id=int(user_id)).first()

        if not user_exist or not patient:
            abort(404, message="Patient not found.")
        
        try:
            return {
                'patient_public_id': patient.public_id,
                "full_name": patient.full_name,
                'email': user_exist.email,
                'is_active': user_exist.is_active,
                'role': "patient",
                "dob": patient.dob.strftime("%Y-%m-%d"),
                "gender": patient.gender,
                "height_cm": patient.height_cm,
                "weight_kg": patient.weight_kg,
                "contact": patient.contact
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) PatientDashboard: (triggered) an error: {e}")
            abort(500, message="Patient data fetching failed.")

class PatientAvailableDoctors(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the list of all currently available doctors data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        try:
            doctors = Doctor.query.all()

            doctor_data = []
            for d in doctors:
                t = User.user_email(d.user_id)
                if t[1] == True: # if the doctor is active
                    doctor_data.append(
                        {
                            'doctor_public_id': d.public_id,
                            'full_name': d.full_name,
                            'email': t[0],
                            'department': Departments_Doctors.dept_name(d.id),
                            'specialization': Specialization.spec_name(d.specialization_id),
                            'gender': d.gender.title(),
                            'license': d.license,
                            'experience': d.experience,
                            'description': d.description,
                            'contact': d.contact
                        }
                    )

            return {
                "count": len(doctor_data),
                "doctors": doctor_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientAvailableDoctors: (triggered) an error: {e}")
            abort(500, message="Doctors data fetching failed.")

class PatientBookAppointment(Resource):
    '''This resource consist of 'GET' & 'POST' method which checks 'access token' sent by the client and handle the appointment booking for the patient as per the request'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        doc_public_id = request.args.get("doctor_public_id")
        try:
            doc_public_id = non_empty_string(doc_public_id, "doctor_public_id parameter")
        except ValueError as e:
            abort(400, message=e)

        doctor = Doctor.query.filter_by(public_id=doc_public_id).first()
        if not doctor:
             abort(404, message="Doctor not found.")
        
        try:
            availabilities = Availability.query.filter_by(doctor_id=doctor.id).all()

            current_datetime = datetime.now()
            weekday_index = int(current_datetime.strftime("%u")) - 1
            current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
            current_week_end_date = current_week_start_date + timedelta(days=6)

            availability_data = []

            # If the availability for the current week is assigned for the doctor
            if availabilities[0].date == current_week_start_date:          
                index_count = 1
                slot_count = 0
                temp = {}
                for a in availabilities:    
                    if int(a.date.strftime("%u")) == index_count:

                        slot_availability = Availability.check_status(doctor.id, a.slot_id)

                        # If the availability date is already passed from the current date
                        if current_datetime.date() > a.date:
                            slot_availability = False

                        if index_count not in temp:
                            temp = {
                                index_count : 
                                    {
                                        "date": a.date.strftime("%Y-%m-%d"),
                                        "weekday": a.date.strftime("%A"),
                                        "slots": [
                                            {
                                                "slot_id": a.slot_id,
                                                "start_time": a.start_time.strftime("%H:%M"),
                                                "end_time": a.end_time.strftime("%H:%M"),
                                                "status": slot_availability
                                            }
                                        ]
                                    }
                                }
                            slot_count += 1
                        else:
                            temp[index_count]["slots"].append(
                                {
                                    "slot_id": a.slot_id,
                                    "start_time": a.start_time.strftime("%H:%M"),
                                    "end_time": a.end_time.strftime("%H:%M"),
                                    "status": slot_availability
                                }
                            )
                            slot_count += 1

                    if slot_count == 3:
                        availability_data.append(
                            temp[index_count]
                        )
                        index_count += 1
                        slot_count = 0
                        temp = {}

            return {
                "doctor_name": doctor.full_name,
                "doctor_public_id": doc_public_id,
                "count": len(availability_data),
                "week_start_date": current_week_start_date.strftime("%Y-%m-%d"),
                "week_end_date": current_week_end_date.strftime("%Y-%m-%d"),
                "availabilities": availability_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientBookAppointment: 'GET' (triggered) an error: {e}")
            abort(500, message="Doctor availability fetching failed.")

    @jwt_required()
    def post(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")
        
        args = patientAppointmentsData_validator.parse_args()

        doctor = Doctor.query.filter_by(public_id=args["doctor_public_id"]).first()
        if not doctor:
            abort(404, message="Doctor not found.")

        # If the slot booking time in the past or future
        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
        current_week_end_date = current_week_start_date + timedelta(days=6)
        if args["slot_date"] < current_datetime.date():
            abort(409, message="Appointment date cannot be in the past.")
        if args["slot_date"] > current_week_end_date:
            abort(409, message="Appointment date cannot be in the future.")

        # Checks for current doctor availability before the appointment booking
        doc_availability = Availability.query.filter_by(doctor_id=doctor.id, slot_id=args["slot_id"]).first()
        if doc_availability:
            if not doc_availability.status:
                abort(409, message="Doctor currently unavailable for the time slot please refresh.")
            if doc_availability.appointments_count >= doc_availability.diagonisis_limit:
                abort(409, message="Doctor's max appointment count reached for the time slot.")
        
        # If the patient has a already pending appointment to the respective doctor
        appointment_exist = Appointment.query.filter_by(
            doctor_id=doctor.id, patient_id=patient.id, 
            status="booked").first()
        
        if appointment_exist:
            abort(409, message="Appointment already booked for these week.")
        
        # If the appointment completed for a selected time slot
        appointment_complete = Appointment.query.filter_by(
            doctor_id=doctor.id, patient_id=patient.id, 
            date=args["slot_date"], start_time=args["slot_start_time"], 
            status="completed").first()
        
        if appointment_complete:
            abort(409, message="Appointment already completed for the selected time slot.")

        try:
            new_appointment = Appointment(
                patient_id = patient.id,
                doctor_id = doctor.id,
                date = args["slot_date"],
                start_time = args["slot_start_time"],
                end_time = args["slot_end_time"],
            )
            db.session.add(new_appointment)
            db.session.flush()

            # Increase Doctors appointment count for the time slot
            doc_availability.appointments_count += 1
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) PatientBookAppointment: 'POST' (triggered) an error: {e}")
            abort(500, message="Patient appointment booking failed.")
        else:
            db.session.commit()
            return {
                "message": "Patient appointment booked successfully."
            }, 200
        

