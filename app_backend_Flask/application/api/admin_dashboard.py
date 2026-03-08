from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from datetime import datetime, timedelta
import os

from app_backend_Flask.application.db_extensions import db
from app_backend_Flask.application import data_cache
from app_backend_Flask.application.models import *
from app_backend_Flask.application.utils.input_validators import *

### Request Parser setup 
## For Apponitment Data
adminAppointmentsData_validator = reqparse.RequestParser()
adminAppointmentsData_validator.add_argument("appointment_public_id", type=non_empty_string, required=True, help="{error_msg}")
adminAppointmentsData_validator.add_argument("status", type=non_empty_string, required=True, help="{error_msg}")

## For Doctor Data
doctorBlockData_validator = reqparse.RequestParser()
doctorBlockData_validator.add_argument("doctor_user_id", type=is_integer, required=True, help="{error_msg}")
doctorBlockData_validator.add_argument("is_active", type=bool, required=True, help="Missing required parameter in the JSON body or not a boolean or empty.")

doctorEditData_validator = reqparse.RequestParser()
doctorEditData_validator.add_argument("doctor_id", type=is_integer, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("full_name", type=check_full_name, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("license", type=non_empty_string, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("qualification", type=non_empty_string, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("specialization_id", type=is_integer, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("experience", type=is_integer, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("department_id", type=is_integer, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("description", type=non_empty_string, required=True, help="{error_msg}")
doctorEditData_validator.add_argument("contact", type=is_valid_contact, required=True, help="{error_msg}")

## For Patient Data
patientBlockData_validator = reqparse.RequestParser()
patientBlockData_validator.add_argument("patient_user_id", type=is_integer, required=True, help="{error_msg}")
patientBlockData_validator.add_argument("is_active", type=bool, required=True, help="Missing required parameter in the JSON body or not a boolean or empty.")

patientEditData_validator = reqparse.RequestParser()
patientEditData_validator.add_argument("patient_id", type=is_integer, required=True, help="{error_msg}")
patientEditData_validator.add_argument("full_name", type=check_full_name, required=True, help="{error_msg}")
patientEditData_validator.add_argument("gender", type=check_gender, required=True, help="{error_msg}")
patientEditData_validator.add_argument("dob", type=is_valid_date, required=True, help="{error_msg}")
patientEditData_validator.add_argument("height_cm", type=is_integer, required=True, help="{error_msg}")
patientEditData_validator.add_argument("weight_kg", type=is_integer, required=True, help="{error_msg}")
patientEditData_validator.add_argument("contact", type=is_valid_contact, required=True, help="{error_msg}")


# Admin Dashboard handler API
class AdminDashboard(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with admin data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            abort(404, message="Admin not found.")

        try:
            return {
                "email": user.email,
                "is_active": user.is_active,
                "role": 'admin',
                "name": 'PentaFlow Admin'
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) AdminDashboard: (triggered) an error: {e}")
            abort(500, message="Admin data fetching failed.")

class AdminAppointments(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handles the appointments as per the request'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        duration = request.args.get("duration")
        try:
            duration = non_empty_string(duration, "'duration' parameter")
            if duration not in ['previous', 'current-week', 'all']:
                raise ValueError("'duration' parameter can only have value 'all' or 'current-week' or 'previous'.")
        except ValueError as e:
            abort(400, message=str(e))


        appointments = []
        current_datetime = datetime.now()
        
        if duration in ["current-week", "previous"]:
            
            weekday_index = int(current_datetime.strftime("%u")) - 1
            current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)

            # Current weeks all appointments list
            if duration == "current-week":
                for i in range(0,7):
                    ap_date = current_week_start_date + timedelta(days=i)
                    ap = Appointment.query.filter_by(date=ap_date).all()
                    appointments += ap
            # All appointments list before the current week
            else:
                appointments = Appointment.query.filter(Appointment.date < current_week_start_date).all()
            
        else:
            # Past all appointments
            appointments = Appointment.query.all()
        
        try:
            appointments_data = []
            booked_appointments_data = []
            for ap in appointments:
                patient = Patient.query.filter_by(id=ap.patient_id).first()
                doctor = Doctor.query.filter_by(id=ap.doctor_id).first()
                if doctor and patient:
                    if ap.status == "booked" and duration == "current-week":
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

            if duration == "current-week":
                return {
                    "count": len(appointments_data),
                    "week_start_date": current_week_start_date.strftime("%Y-%m-%d"),
                    "week_end_date": (current_week_start_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                    "appointments": appointments_data
                }, 200
            else:
                appointments_data.reverse()
                return {
                    "count": len(appointments_data),
                    "appointments": appointments_data
                }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminAppointments: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient and doctor upcoming appointments fetching failed.")

    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        args = adminAppointmentsData_validator.parse_args()

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
            app.logger.exception(f"(Resource) AdminAppointments: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Appointment status patching failed.")
        else:
            db.session.commit()
            return {
                "message": "Appointment status updated successfully."
            }, 200

class AdminPatientsData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the list of all current patient data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        try:
            patients = data_cache.get_all_patients()

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
            app.logger.exception(f"(Resource) AdminPatientsData: (triggered) an error: {e}")
            abort(500, message="Patients data fetching failed.")

class AdminPatientAppointmentHistory(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and sends back the patient appointment history'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        pat_public_id = request.args.get("patient_public_id")
        try:
            patient_public_id = non_empty_string(pat_public_id)
        except ValueError:
            abort(400, message="'patient_public_id' parameter should be an string and not empty.")

        patient = Patient.query.filter_by(public_id=patient_public_id).first()
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
            app.logger.exception(f"(Resource) AdminPatientAppointmentHistory: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient past appointment history data fetching failed.")

class AdminPatientTreatmentData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and sends back the appointment treatment data if exist'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

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
            app.logger.exception(f"(Resource) AdminPatientTreatmentData: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient Appointment Treatment data fetching failed.")

class AdminDoctorsData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the list of all current doctor data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        try:
            doctors = data_cache.get_all_doctors()
            
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
                        'qualification': d.qualification,
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
            app.logger.exception(f"(Resource) AdminDoctorsData: (triggered) an error: {e}")
            abort(500, message="Doctors data fetching failed.")

class StatsCount(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the current count of the doctors, patients, and pending appointments'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
            
        try:   
            doc_count = Doctor.query.count()
            patient_count = Patient.query.count()
            # Total Appointment Count
            appointment_count = Appointment.query.count()

            return {
                "appointment_count": appointment_count,
                "doctor_count": doc_count,
                "patient_count": patient_count
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) StatsCount: (triggered) an error: {e}")
            abort(500, message="Stats count fetching failed.")

class DepartmentList(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with all the available departments'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
            
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
            app.logger.exception(f"(Resource) DepartmentList: (triggered) an error: {e}")
            abort(500, message="Departments list fetching failed.")

class SpecializationList(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with all the available specializations'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
            
        try:   
            specializations = Specialization.query.all()

            spec_data = []
            for s in specializations:
                spec_data.append(
                    {
                        'id': s.id,
                        'name': s.name
                    }
                )

            return {
                "count": len(spec_data),
                "specializations": spec_data
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) DepartmentList: (triggered) an error: {e}")
            abort(500, message="Departments list fetching failed.")
        
class AdminManageDoctor(Resource):
    '''This resource consist of 'GET','POST','PATCH' & 'DELETE' method which checks 'access token' sent by the client and handle the doctor as per the request'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        doc_id = request.args.get("doctor_id")
        try:
            doctor_id = is_integer(doc_id)
        except ValueError:
            abort(400, message="'doctor_id' parameter should be an integer and not empty.")

        doctor = Doctor.query.filter_by(id=doctor_id).first()
        if not doctor:
             abort(404, message="Doctor not found.")

        try:
            t = User.user_email(doctor.user_id)
            doc_dept = Departments_Doctors.query.filter_by(doctor_id=doctor.id).first()
            return {
                    'doctor_id': doctor.id,
                    'doctor_public_id': doctor.public_id,
                    'user_id': doctor.user_id,
                    'full_name': doctor.full_name,
                    'email': t[0],
                    'is_active': t[1],
                    'specialization_id': doctor.specialization_id,
                    'department_id': doc_dept.department_id,
                    'gender': doctor.gender,
                    'license': doctor.license,
                    'qualification': doctor.qualification,
                    'experience': doctor.experience,
                    'description': doctor.description,
                    'contact': doctor.contact
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminManageDoctor: 'GET' (triggered) an error: {e}")
            abort(500, message="Doctor data fetching failed.")

    @jwt_required()   
    def post(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        if not request.is_json:
            abort(400, message="Only JSON data allowed")

        args = doctorBlockData_validator.parse_args()

        user_role = Roles_Users.user_role(int(args["doctor_user_id"]))
        if user_role == "admin":
            abort(400, message=f"Admin cannot be {'unblocked' if args['is_active'] else 'blocked'}.")
        elif user_role == "patient":
            abort(400, message=f"Patient cannot be {'unblocked' if args['is_active'] else 'blocked'}.")

        doctor = User.query.filter_by(id=int(args["doctor_user_id"])).first()
        if not doctor:
            abort(404, message="Doctor user donot exist.")

        doc = Doctor.query.filter_by(user_id=int(args["doctor_user_id"])).first()
        if not doc:
            abort(404, message="Doctor donot exist.")
        else:
            doc_id = doc.id

        try:
            if doctor.is_active != args['is_active']:
                if not args['is_active']:
                    doctor.is_active = False
                    db.session.flush()

                    # Invalidate all the existing tokens
                    tokens = User_Tokens.query.filter_by(user_id=int(args["doctor_user_id"])).all()
                    for t in tokens:
                        t.valid = False
                        db.session.flush()

                    # Cancel all existing booked appointments
                    appointments = Appointment.query.filter_by(doctor_id=doc_id, status="booked").all()
                    for ap in appointments:
                        ap.status = "canceled"
                        db.session.flush()
                else:
                    doctor.is_active = True
                    db.session.flush()
                
                app.extensions["cache_data"].delete("doctor_cache")
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManageDoctor: 'POST' (triggered) an error: {e}")
            abort(500, message=f"Doctor {'unblocking' if args['is_active'] else 'blocking'} failed.")
        else:
            db.session.commit()
            return {"message": f"Doctor {'unblocked' if args['is_active'] else 'blocked'} successfully."}, 200
        
    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(403, message="Admin access needed")
       
        args = doctorEditData_validator.parse_args()

        doctor_exist = Doctor.query.filter_by(id=args["doctor_id"]).first()
        if not doctor_exist:
            abort(404, message="Doctor not found")
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
        if Doctor.query.filter(Doctor.id != args["doctor_id"], Doctor.license == args["license"]).first():
            abort(400, message={
                'license': "License provided already exist"
            })
        
        try:

            doctor_exist.full_name = args["full_name"].title()
            doctor_exist.gender = args["gender"]
            doctor_exist.license = args["license"]
            doctor_exist.qualification = args["qualification"].upper()
            doctor_exist.specialization_id = args["specialization_id"]
            doctor_exist.experience = args["experience"]
            doctor_exist.description = args["description"]
            doctor_exist.contact = args["contact"]
            
            db.session.flush()

            dept_doc = Departments_Doctors.query.filter_by(doctor_id=args["doctor_id"]).first()
            if dept_doc:
                dept_doc.department_id = args["department_id"]
                db.session.flush()
            else:
                raise Exception("Doctor id not found in the departments_doctors joining table.")
            
            app.extensions["cache_data"].delete("doctor_cache")
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManageDoctor: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Doctor edit failed")
        else:
            db.session.commit()
            return {'message': "Doctor edited successfully."}, 200

    @jwt_required()   
    def delete(self):
        
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        doc_user_id = request.args.get("doctor_user_id")
        try:
            doctor_user_id = is_integer(doc_user_id)
        except ValueError:
            abort(400, message="'doctor_user_id' parameter should be an integer and not empty.")


        user_role = Roles_Users.user_role(doctor_user_id)
        if user_role == "admin":
            abort(400, message="Admin cannot be deleted.")
        elif user_role == "patient":
            abort(400, message="Patient cannot be deleted.")

        doctor = User.query.filter_by(id=doctor_user_id).first()
        if not doctor:
             abort(404, message="Doctor donot exist.")

        doc_exist = Doctor.query.filter_by(user_id=doctor_user_id).first()
        if doc_exist:
            doc_public_id = doc_exist.public_id
        else:
            doc_public_id = None

        try:
            db.session.delete(doctor)
            db.session.flush()

            app.extensions["cache_data"].delete("doctor_cache")

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManageDoctor: 'DELETE' (triggered) an error: {e}")
            abort(500, message="Doctor deletion failed.")
        else:
            db.session.commit()

            try:
                if doc_public_id and os.path.exists(f"./doctor_credentials/{doc_public_id}_cred.txt"):
                    os.remove(f"./doctor_credentials/{doc_public_id}_cred.txt")
            except Exception as e:
                app.logger.exception(f"Doctor with public id {doc_public_id} credential file removal failed (cause): {e}")

            return {"message": "Doctor deleted successfully."}, 204    
        
class AdminManagePatient(Resource):
    '''This resource consist of 'GET','POST','PATCH' & 'DELETE' method which checks 'access token' sent by the client and handle the patient as per the request'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        pat_id = request.args.get("patient_id")
        try:
            patient_id = is_integer(pat_id)
        except ValueError:
            abort(400, message="'patient_id' parameter should be an integer and not empty.")

        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
             abort(404, message="Patient not found.")
        
        try:
            t = User.user_email(patient.user_id)
            return {
                    'patient_id': patient.id,
                    'patient_public_id': patient.public_id,
                    'user_id': patient.user_id,
                    'full_name': patient.full_name,
                    'email': t[0],
                    'is_active': t[1],
                    'gender': patient.gender,
                    'dob': patient.dob.strftime("%Y-%m-%d"),
                    'height_cm': patient.height_cm,
                    'weight_kg': patient.weight_kg,
                    'contact': patient.contact
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminManagePatient: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient data fetching failed.")

    @jwt_required()   
    def post(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        if not request.is_json:
            abort(400, message="Only JSON data allowed")

        args = patientBlockData_validator.parse_args()

        user_role = Roles_Users.user_role(int(args["patient_user_id"]))
        if user_role == "admin":
            abort(400, message=f"Admin cannot be {'unblocked' if args['is_active'] else 'blocked'}.")
        elif user_role == "doctor":
            abort(400, message=f"Doctor cannot be {'unblocked' if args['is_active'] else 'blocked'}.")

        patient = User.query.filter_by(id=int(args["patient_user_id"])).first()
        if not patient:
             abort(404, message="Patient donot exist.")

        try:
            if patient.is_active != args['is_active']:
                if not args['is_active']:
                    patient.is_active = False
                    db.session.flush()
                    # Invalidate all the existing tokens
                    tokens = User_Tokens.query.filter_by(user_id=int(args["patient_user_id"])).all()
                    for t in tokens:
                        t.valid = False
                        db.session.flush()
                else:
                    patient.is_active = True
                    db.session.flush()
                
                app.extensions["cache_data"].delete("patient_cache")
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManagePatient: 'POST' (triggered) an error: {e}")
            abort(500, message=f"Patient {'unblocking' if args['is_active'] else 'blocking'} failed.")
        else:
            db.session.commit()
            return {"message": f"Patient {'unblocked' if args['is_active'] else 'blocked'} successfully."}, 200
        
    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(403, message="Admin access needed")
       
        args = patientEditData_validator.parse_args()

        patient_exist = Patient.query.filter_by(id=args["patient_id"]).first()
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
            app.extensions["cache_data"].delete("patient_cache")
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManagePatient: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Patient edit failed.")
        else:
            db.session.commit()
            return {'message': "Patient edited successfully."}, 200

    @jwt_required()   
    def delete(self):
        
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        pat_user_id = request.args.get("patient_user_id")
        try:
            patient_user_id = is_integer(pat_user_id)
        except ValueError:
            abort(400, message="'patient_user_id' parameter should be an integer and not empty.")

        user_role = Roles_Users.user_role(patient_user_id)
        if user_role == "admin":
            abort(400, message="Admin cannot be deleted.")
        elif user_role == "doctor":
            abort(400, message="Doctor cannot be deleted.")

        patient = User.query.filter_by(id=patient_user_id).first()
        if not patient:
             abort(404, message="Patient donot exist.")

        try:
            db.session.delete(patient)
            db.session.flush()
            app.extensions["cache_data"].delete("patient_cache")

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminManagePatient: 'DELETE' (triggered) an error: {e}")
            abort(500, message="Patient deletion failed.")
        else:
            db.session.commit()
            return {"message": "Patient deleted successfully."}, 204    