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

## Request Parsers

# For Patient profile update Data
patientProfileEditData_validator = reqparse.RequestParser()
patientProfileEditData_validator.add_argument("patient_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("full_name", type=check_full_name, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("dob", type=is_valid_date, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("height_cm", type=is_integer, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("weight_kg", type=is_integer, required=True, help="{error_msg}")
patientProfileEditData_validator.add_argument("contact", type=is_valid_contact, required=True, help="{error_msg}")

# For Patient Booking Appointments Data
patientBookAppointmentData_validator = reqparse.RequestParser()
patientBookAppointmentData_validator.add_argument("doctor_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientBookAppointmentData_validator.add_argument("slot_id", type=non_empty_string, required=True, help="{error_msg}")
patientBookAppointmentData_validator.add_argument("slot_date", type=is_valid_date, required=True, help="{error_msg}")
patientBookAppointmentData_validator.add_argument("slot_start_time", type=is_valid_time, required=True, help="{error_msg}")
patientBookAppointmentData_validator.add_argument("slot_end_time", type=is_valid_time, required=True, help="{error_msg}")

# For Patient Appointment Manage Data
patientAppointmentsData_validator = reqparse.RequestParser()
patientAppointmentsData_validator.add_argument("appointment_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientAppointmentsData_validator.add_argument("status", type=non_empty_string, required=True, help="{error_msg}")

# Patient Dashboard handler API
class PatientDashboard(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handles the respective patient data as requested'''
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

    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(403, message="Patient access needed")
       
        args = patientProfileEditData_validator.parse_args()

        patient_exist = Patient.query.filter_by(public_id=args["patient_public_id"]).first()
        if not patient_exist:
            abort(404, message="Patient not found")
        
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
            patient_exist.full_name = args["full_name"].title()
            patient_exist.gender = args["gender"]
            patient_exist.dob = dob
            patient_exist.height_cm = args["height_cm"]
            patient_exist.weight_kg = args["weight_kg"]
            patient_exist.contact = args["contact"]
            
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) PatientDashboard: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Patient edit failed.")
        else:
            db.session.commit()
            return {'message': "Patient edited successfully."}, 200
        
class PatientAvailableDoctors(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the list of all currently available doctors data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        dept_name = request.args.get("department")
        try:
            dept_name = non_empty_string(dept_name)
        except ValueError:
            abort(400, message="'department' parameter should be an string and not empty.")

        if dept_name != 'all':
            department = Department.query.filter_by(name=dept_name).first()
            if not department:
                abort(404, message="Department not exist.")

        try:
            if dept_name != 'all':
                doctors_id = [d.doctor_id for d in (Departments_Doctors.query.filter_by(department_id=department.id).all())]
            else:
                doctors_id = [d.doctor_id for d in (Departments_Doctors.query.all())]

            doctors_data = []
            
            for dId in doctors_id:
                doc = Doctor.query.filter_by(id=dId).first()
                if doc:
                    t = User.user_email(doc.user_id)
                    if t[1] == True: # if the doctor is active
                        doctors_data.append(
                            {
                                'doctor_public_id': doc.public_id,
                                'full_name': doc.full_name,
                                'department': Departments_Doctors.dept_name(doc.id),
                                'specialization': Specialization.spec_name(doc.specialization_id),
                                'qualification': doc.qualification,
                                'gender': doc.gender.title(),
                                'license': doc.license,
                                'experience': doc.experience,
                                'description': doc.description,
                            }
                        )

            return {
                "count": len(doctors_data),
                "department": dept_name,
                "doctors": doctors_data
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
        
        args = patientBookAppointmentData_validator.parse_args()

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
            abort(409, message="Appointment already booked for this week.")
        
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
        
class PatientUpcomingAppointments(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handle the patient upcoming appointments as per the request'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")

        # Current weeks appointments list
        appointments = []

        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
        for i in range(0,7):
            ap_date = current_week_start_date + timedelta(days=i)
            ap = Appointment.query.filter_by(patient_id=patient.id, date=ap_date).all()
            appointments += ap
        
        try:
            appointments_data = []
            booked_appointments_data = []
            for ap in appointments:
                doctor = Doctor.query.filter_by(id=ap.doctor_id).first()
                if doctor:
                    if ap.status == "booked":
                        booked_appointments_data.append(
                            {
                                'appointment_public_id': ap.public_id,
                                'patient_public_id': patient.public_id,
                                'patient_full_name': patient.full_name,
                                'doctor_full_name': doctor.full_name,
                                'doctor_public_id': doctor.public_id,
                                'doctor_department': Departments_Doctors.dept_name(doctor.id),
                                'date': ap.date.strftime("%Y-%m-%d"),
                                'start_time': ap.start_time.strftime("%H:%M"),
                                'end_time': ap.end_time.strftime("%H:%M"),
                                'status': ap.status,
                            }
                        )
                    else:
                        appointments_data.append(
                            {
                                'appointment_public_id': ap.public_id,
                                'patient_public_id': patient.public_id,
                                'patient_full_name': patient.full_name,
                                'doctor_full_name': doctor.full_name,
                                'doctor_public_id': doctor.public_id,
                                'doctor_department': Departments_Doctors.dept_name(doctor.id),
                                'date': ap.date.strftime("%Y-%m-%d"),
                                'start_time': ap.start_time.strftime("%H:%M"),
                                'end_time': ap.end_time.strftime("%H:%M"),
                                'status': ap.status,
                            }
                        )
                    
            appointments_data = booked_appointments_data + appointments_data

            return {
                "count": len(appointments_data),
                "week_start_date": current_week_start_date.strftime("%Y-%m-%d"),
                "week_end_date": (current_week_start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                "appointments": appointments_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientUpcomingAppointments: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient upcoming appointments fetching failed.")

    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")
        
        args = patientAppointmentsData_validator.parse_args()

        if args["status"].lower() != "canceled":
            abort(400, message={
                "status": "Value can only be 'canceled'."
            })

        appoint = Appointment.query.filter_by(public_id=args["appointment_public_id"]).first()
        if appoint:
            if appoint.status == "canceled":
                abort(409, message="Appointment already canceled.")
            elif appoint.status == "completed":
                abort(409, message="Appointment already completed.")
        else:
            abort(404, message="Appointment not exist.")
        
        try:
            appoint.status = args["status"].lower()
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) PatientUpcomingAppointments: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Appointment status patching failed.")
        else:
            db.session.commit()
            return {
                "message": "Appointment status updated successfully."
            }, 200
        
class PatientDepartmentList(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with all the available departments'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")
            
        try:   
            departments = Department.query.all()

            dept_data = []
            for d in departments:
                dept_data.append(
                    {
                        'id': d.id,
                        'name': d.name,
                        'description': d.description,
                        'type': d.type
                    }
                )

            return {
                "count": len(dept_data),
                "departments": dept_data
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) PatientDepartmentList: (triggered) an error: {e}")
            abort(500, message="Departments list fetching failed.")

class PatientAppointmentHistory(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and handle the patient completed appointment history as per the request'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
            abort(404, message="Patient not found.")


        appointments = Appointment.query.filter_by(patient_id=patient.id, status="completed").all()
        
        try:
            pat_appointments_history = []

            for ap in appointments:
                ap_doc = Doctor.query.filter_by(id=ap.doctor_id).first()
                if not ap_doc:
                    doc_name = "Unknown"
                    doc_pub_id = "NA"
                    doc_dept = "NA"
                else:
                    doc_name = ap_doc.full_name
                    doc_pub_id = ap_doc.public_id
                    doc_dept = Departments_Doctors.dept_name(ap_doc.id)

                pat_appointments_history.append(
                    {
                        'appointment_public_id': ap.public_id,
                        'doctor_full_name': doc_name,
                        'doctor_public_id': doc_pub_id,
                        'doctor_department': doc_dept,
                        'date': ap.date.strftime("%Y-%m-%d"),
                        'start_time': ap.start_time.strftime("%H:%M"),
                        'end_time': ap.end_time.strftime("%H:%M"),
                    }
                )

            pat_appointments_history.reverse()
            return {
                "count": len(pat_appointments_history),
                "patient_public_id": patient.public_id,
                "patient_full_name": patient.full_name,
                "patient_history": pat_appointments_history
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientAppointmentHistory: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient Appointment History data fetching failed.")

class PatientTreatmentData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and sends back the appointment treatment data if exist'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")

        ap_public_id = request.args.get("appointment_public_id")
        try:
            ap_public_id = non_empty_string(ap_public_id)
        except ValueError:
            abort(400, message="'appointment_public_id' parameter should be an string and not empty.")

        appointment = Appointment.query.filter_by(public_id=ap_public_id).first()
        if not appointment:
             abort(404, message="Appointment not found.")

        try:
            ap_treatment_data = Treatment.query.filter_by(appointment_id=appointment.id).first()

            if ap_treatment_data == None:
                return {
                    'appointment_public_id': ap_public_id,
                    "status": "unavailable"
                }, 200
            
            else:
                return {
                    'appointment_public_id': ap_public_id,
                    'visit_type': ap_treatment_data.visit_type,
                    'test_done': ap_treatment_data.test_done,
                    'diagnosis': ap_treatment_data.diagnosis,
                    'prescription': ap_treatment_data.prescription,
                    'medicine': ap_treatment_data.medicine,
                    'notes': ap_treatment_data.notes,
                    "status": "available"
                }, 200
                
        except Exception as e:
            app.logger.exception(f"(Resource) PatientTreatmentData: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient Appointment Treatment data fetching failed.")
