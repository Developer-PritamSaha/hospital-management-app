from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from ..extensions import db
from app_backend_Flask.application.models import *
from app_backend_Flask.application import celery_tasks
from ..utils.input_validators import *

## For Doctor Availability Data
doctorAvailabilityData_validator = reqparse.RequestParser()
doctorAvailabilityData_validator.add_argument("slot_id", type=non_empty_string, required=True, help="{error_msg}")
doctorAvailabilityData_validator.add_argument("patient_cap", type=is_integer, required=True, help="{error_msg}")
doctorAvailabilityData_validator.add_argument("status", type=bool, required=True, help="Missing required parameter in the JSON body or not a boolean or empty.")

## For Doctor Appointment Data
doctorAppointmentData_validator = reqparse.RequestParser()
doctorAppointmentData_validator.add_argument("appointment_public_id", type=non_empty_string, required=True, help="{error_msg}")
doctorAppointmentData_validator.add_argument("status", type=non_empty_string, required=True, help="{error_msg}")

## For Patient Treatment Data
patientTreatmentData_validator = reqparse.RequestParser()
patientTreatmentData_validator.add_argument("appointment_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("visit_type", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("test_done", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("diagnosis", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("prescription", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("medicine", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentData_validator.add_argument("notes", type=non_empty_string, required=True, help="{error_msg}")

## For Patient Treatment Edit Data
patientTreatmentEditData_validator = reqparse.RequestParser()
patientTreatmentEditData_validator.add_argument("appointment_public_id", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("visit_type", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("test_done", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("diagnosis", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("prescription", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("medicine", type=non_empty_string, required=True, help="{error_msg}")
patientTreatmentEditData_validator.add_argument("notes", type=non_empty_string, required=True, help="{error_msg}")


# Doctor Dashboard handler API
class DoctorDashboard(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with respective doctor data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        user_exist = User.query.filter_by(id=int(user_id)).first()
        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()

        if not user_exist or not doctor:
            abort(404, message="Doctor not found.")

        # is_updated = reset_weekly_dates(doctor.id)
        
        try:
            return {
                'doctor_public_id': doctor.public_id,
                'full_name': doctor.full_name,
                'email': user_exist.email,
                'is_active': user_exist.is_active,
                'role': "doctor",
                'department': Departments_Doctors.dept_name(doctor.id),
                'specialization': Specialization.spec_name(doctor.specialization_id),
                'qualification': doctor.qualification,
                'gender': doctor.gender.title(),
                'license': doctor.license,
                'experience': doctor.experience,
                'description': doctor.description,
                'contact': doctor.contact,
                # 'availability_updated': is_updated
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) DoctorDashboard: (triggered) an error: {e}")
            abort(500, message="Doctor data fetching failed.")

class DocStatsCount(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the current count of the total appointments, completed, canceled for the week '''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
             abort(404, message="Doctor not found.")

        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        new_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
            
        ap_count = 0
        completed_count = 0
        canceled_count = 0

        try:   
            for d_count in range(0,7):
                d = new_week_start_date + timedelta(days=d_count)
                ap = Appointment.query.filter_by(doctor_id=doctor.id,date=d).all()
                
                for a in ap:
                    if a.status == "completed":
                        completed_count += 1
                    elif a.status == "canceled":
                        canceled_count += 1
                    else:
                        ap_count += 1

            return {
                "appointment_count": ap_count,
                "completed_count": completed_count,
                "canceled_count": canceled_count
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) DocStatsCount: (triggered) an error: {e}")
            abort(500, message="Doctors current weeks stats count fetching failed.")

def reset_weekly_dates(doc_id: int):
    '''Reassigns the new weekly dates for the existing availability schedules for the respective doctors'''
    current_datetime = datetime.now()
    weekday_index = int(current_datetime.strftime("%u")) - 1
    new_week_start_date = current_datetime.date() - timedelta(days=weekday_index)

    doc_avail1 = Availability.query.filter_by(doctor_id=doc_id,slot_id="d1s1").first()
    prev_week_start_date = doc_avail1.date
    if prev_week_start_date != new_week_start_date:
        try:
            availabilities = Availability.query.filter_by(doctor_id=doc_id).all()
            temp_slot_count = 0
            days_count = 0
            for a in availabilities:
                # Each day has three time slots
                if temp_slot_count == 3:
                    temp_slot_count = 0
                    days_count += 1

                a.date = new_week_start_date + timedelta(days=days_count)
                a.appointments_count = 0
                db.session.flush()

                temp_slot_count += 1

                # Cancel the previous week pending appointments
                if temp_slot_count == 3:
                    prev_week_pending_appointments = Appointment.query.filter_by(
                        doctor_id = doc_id, 
                        date = prev_week_start_date + timedelta(days=days_count), 
                        status = "booked"
                    ).all()
                    
                    if len(prev_week_pending_appointments) > 0:
                        for pending in prev_week_pending_appointments:
                            pending.status = "canceled"
                            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) DoctorManageAvailability.reset_weekly_dates(): (triggered) doctor availability weekly date update rollback (cause): {e}")
            return False
        else:
            db.session.commit()
            return True
    else:
        return False

class DoctorManageAvailability(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handle the availability for the doctor as per the request'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")
            
        reset_weekly_dates(doctor.id)
        
        try:
            availabilities = Availability.query.filter_by(doctor_id=doctor.id).all()

            availability_data = []
            index_count = 1
            slot_count = 0
            temp = {}
            for a in availabilities:    
                if int(a.date.strftime("%u")) == index_count:
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
                                            "diagonisis_limit": a.diagonisis_limit,
                                            "status": a.status
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
                                "diagonisis_limit": a.diagonisis_limit,
                                "status": a.status
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
                "count": len(availability_data),
                "week_start_date": availabilities[0].date.strftime("%Y-%m-%d"),
                "week_end_date": availabilities[20].date.strftime("%Y-%m-%d"),
                "availabilities": availability_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) DoctorManageAvailability: 'GET' (triggered) an error: {e}")
            abort(500, message="Doctor availability fetching failed.")

    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")
        
        args = doctorAvailabilityData_validator.parse_args()

        current_datetime = datetime.now()
        weekday_index = int(current_datetime.strftime("%u")) - 1
        current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)

        temp_avail = Availability.query.filter_by(doctor_id=doctor.id, slot_id="d1s1").first()
        if temp_avail.date != current_week_start_date:
            abort(400, message="Doctor availability dates for the current week has not aloted yet.")

        availability = Availability.query.filter_by(doctor_id=doctor.id, slot_id=args["slot_id"]).first()
        if not availability:
            abort(404, message="Doctor availability slot not found.")

        try:
            if availability.status != args["status"]:
                if not args["status"]:
                    availability.status = False
                    db.session.flush()

                    # If patients already booked the time slot they will be canceled
                    if (availability.appointments_count > 0):
                        appointments = Appointment.query.filter_by(
                            doctor_id = doctor.id, 
                            date = availability.date, 
                            start_time = availability.start_time).all()
                        for ap in appointments:
                            ap.status = "canceled"
                            db.session.flush()

                        availability.appointments_count = 0
                        db.session.flush()
                else:
                    availability.status = True
                    db.session.flush()

            if availability.diagonisis_limit != args["patient_cap"]:
                availability.diagonisis_limit = args["patient_cap"]
                db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorManageAvailability: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Doctor availability status patching failed.")
        else:
            db.session.commit()
            return {
                "message": "Doctor availability status updated successfully."
            }, 200
        
class DoctorManageAppointments(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handle the doctor appointments as per the request'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
             abort(404, message="Doctor not found.")

        duration = request.args.get("duration")
        try:
            duration = non_empty_string(duration, "'duration' parameter")
            if duration not in ['history', 'current-week', 'all']:
                raise ValueError("'duration' parameter can only have value 'all' or 'current-week' or 'history'.")
        except ValueError as e:
            abort(400, message=str(e))


        appointments = []

        if duration in ["current-week", "history"]:
            current_datetime = datetime.now()
            weekday_index = int(current_datetime.strftime("%u")) - 1
            current_week_start_date = current_datetime.date() - timedelta(days=weekday_index)

            # Current weeks all appointments list
            if duration == "current-week":
                for i in range(0,7):
                    ap_date = current_week_start_date + timedelta(days=i)
                    ap = Appointment.query.filter_by(doctor_id=doctor.id, date=ap_date, status='booked').all()
                    appointments += ap
            # All the canceled or completed appointments list
            else:
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.status != "booked"
                ).all()
        else:
            # Past all appointments
            appointments = Appointment.query.filter_by(doctor_id = doctor.id).all()
        
        try:
            appointments_data = []
            for ap in appointments:
                patient = Patient.query.filter_by(id=ap.patient_id).first()

                if patient:
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
            app.logger.exception(f"(Resource) DoctorManageAppointments: 'GET' (triggered) an error: {e}")
            abort(500, message="Doctor upcoming appointments fetching failed.")

    @jwt_required()
    def patch(self):    
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")
        
        args = doctorAppointmentData_validator.parse_args()

        if args["status"].lower() not in ["completed","canceled"]:
            abort(400, message={
                "status": "Value can only be 'completed' or 'canceled'."
            })

        appoint = Appointment.query.filter_by(public_id=args["appointment_public_id"]).first()
        if appoint:
            if appoint.status == "canceled":
                abort(409, message="Appointment already canceled.")
            elif appoint.status == "completed":
                abort(409, message="Appointment already completed.")
            
            is_treatment_updated = Treatment.query.filter_by(appointment_id=appoint.id).first() is not None
            if (not is_treatment_updated) and (args["status"] != "canceled"):
                abort(400, message="Appointment treatment not provided yet.")

            if (datetime.now().date() != appoint.date) and (args["status"] == "completed"):
                abort(400, message="Appointment date and current date donot match.")

        else:
            abort(404, message="Appointment not exist.")
        
        try:
            appoint.status = args["status"].lower()
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorManageAppointments: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Appointment status patching failed.")
        else:
            db.session.commit()
            return {
                "message": "Appointment status updated successfully."
            }, 200
        
class DoctorAssignedPatient(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and send back the list of assigned patient of the doctor'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
             abort(404, message="Doctor not found.")

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
            app.logger.exception(f"(Resource) DoctorAssignedPatient: 'GET' (triggered) an error: {e}")
            abort(500, message="Assigned patients fetching failed.")

class DoctorPatientTreatmentHistory(Resource):
    '''This resource consist of 'GET', 'POST' & 'PATCH' method which checks 'access token' sent by the client and handle the patient treatment history as per the request'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

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
            app.logger.exception(f"(Resource) DoctorPatientTreatmentHistory: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient past Treatment History data fetching failed.")

    @jwt_required()   
    def post(self):
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")
        
        args = patientTreatmentData_validator.parse_args()

        appointment = Appointment.query.filter_by(public_id=args["appointment_public_id"]).first()
        if appointment:
            if appointment.status == "canceled":
                abort(400, message="Appointment already canceled.")
            elif appointment.status == "completed":
                abort(400, message="Appointment already completed.")
        else:
            abort(404, message="Appointment not exist.")

        treatment_exist = Treatment.query.filter_by(appointment_id=appointment.id).first()
        if treatment_exist:
            abort(409, message="Patient treatment history for the appointment already added.")

        try:
            new_treatment = Treatment(
                appointment_id = appointment.id,
                visit_type = args["visit_type"],
                test_done = args["test_done"],
                diagnosis = args["diagnosis"],
                prescription = args["prescription"],
                medicine = args["medicine"],
                notes = args["notes"]
            )

            db.session.add(new_treatment)
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorPatientTreatmentHistory: 'POST' (triggered) an error: {e}")
            abort(500, message="Patient treatment history adding failed.")
        else:
            db.session.commit()
            return {
                "message": "Patient treatment history added successfully."
            }, 200
        
    @jwt_required()   
    def patch(self):
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")
        
        args = patientTreatmentData_validator.parse_args()

        appointment = Appointment.query.filter_by(public_id=args["appointment_public_id"]).first()
        if appointment:
            if appointment.status == "canceled":
                abort(400, message="Appointment already canceled.")
            elif appointment.status == "completed":
                abort(400, message="Appointment already completed.")
        else:
            abort(404, message="Appointment not exist.")

        treatment_exist = Treatment.query.filter_by(appointment_id=appointment.id).first()
        if not treatment_exist:
            abort(404, message="Patient treatment history not found for the appointment.")

        try:
            treatment_exist.visit_type = args["visit_type"]
            treatment_exist.test_done = args["test_done"]
            treatment_exist.diagnosis = args["diagnosis"]
            treatment_exist.prescription = args["prescription"]
            treatment_exist.medicine = args["medicine"]
            treatment_exist.notes = args["notes"]

            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorPatientTreatmentHistory: 'PATCH' (triggered) an error: {e}")
            abort(500, message="Patient treatment history updating failed.")
        else:
            db.session.commit()
            return {
                "message": "Patient treatment history updated successfully."
            }, 200
        
class DoctorPatientAppointmentTreatmentData(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and sends back the treatment data if exist for a given appointment'''

    @jwt_required()   
    def get(self):
        
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        doctor = Doctor.query.filter_by(user_id=int(user_id)).first()
        if not doctor:
            abort(404, message="Doctor not found.")

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
            app.logger.exception(f"(Resource) DoctorPatientAppointmentTreatmentData: 'GET' (triggered) an error: {e}")
            abort(500, message="Patient Appointment Treatment data fetching failed.")
