from flask import request
from flask import current_app as app
from flask_restful import Resource
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_
from datetime import datetime, timedelta

from app_backend_Flask.application.models import *
from ..utils.input_validators import *

class AdminSearchAppointments(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all searched appointments'''
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

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        alt_search_flag = 0
        searched_doctors_id = [-1]
        searched_patients_id = [-1]

        if alt_search_flag == 0:
            # Searches Doctor 
            searched_doctors = Doctor.query.filter(
                or_(
                    Doctor.full_name.contains(search_str),
                    Doctor.public_id.ilike(search_str)
                )
            ).all()

            if len(searched_doctors) > 0:
                searched_doctors_id = [d.id for d in searched_doctors]
                alt_search_flag = 1
                
            # Searches Patient 
            searched_patients = Patient.query.filter(
                or_(
                    Patient.full_name.contains(search_str),
                    Patient.public_id.ilike(search_str)
                )
            ).all()

            if len(searched_patients) > 0:
                searched_patients_id = [p.id for p in searched_patients]
                alt_search_flag = 1

        # Searches for the doctors in departments
        if alt_search_flag == 0:
            searched_department = Department.query.filter(
                Department.name.contains(search_str)
            ).first()

            if searched_department:
                searched_doctors_id = [d.id for d in Departments_Doctors.query.filter_by(department_id = searched_department.id).all()]


        searched_appointments = Appointment.query.filter(
            or_(
                Appointment.doctor_id.in_(searched_doctors_id),
                Appointment.patient_id.in_(searched_patients_id),
                Appointment.date.contains(search_str),
                Appointment.public_id.ilike(search_str),
                Appointment.start_time.contains(search_str),
                Appointment.status.ilike(search_str)
            )
        ).all()

        if len(searched_appointments) == 0:
            abort(404, message="No Search Result Found.")


        appointments = []

        if duration in ["current-week", "previous"]:
            
            current_datetime = datetime.now()
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
                if ap in searched_appointments:
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

            if len(appointments_data) == 0:
                return{ "message":"No Search Result Found."}, 404

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
            app.logger.exception(f"(Resource) AdminSearchAppointments: (GET) (triggered) an error: {e}")
            abort(500, message="Admin appointments search data fetching failed.")

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

        # User active status
        status_search_flag = False
        if search_str.lower() in ["active", "inactive"]:
            patients = Patient.query.all()
            status_search_flag = True
            if search_str == "active":
                active_state = True
            else:
                active_state = False
        else:
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
                if status_search_flag:
                    if active_state == t[1]:  
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
                else:
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


        # User active status
        status_search_flag = False
        if search_str.lower() in ["active", "inactive"]:
            doctors = Doctor.query.all()
            status_search_flag = True
            if search_str == "active":
                active_state = True
            else:
                active_state = False
        else:
            spec = Specialization.query.filter(Specialization.name.contains(search_str)).first()
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
                if status_search_flag: 
                    if active_state == t[1]:  
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
                else:
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

class DoctorSearchAppointments(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all searched appointments'''
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

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        searched_patients_id = [-1]
        searched_patients = Patient.query.filter(
            or_(
                Patient.full_name.contains(search_str),
                Patient.public_id.ilike(search_str)
            )
        ).all()

        if len(searched_patients) > 0:
            searched_patients_id = [p.id for p in searched_patients]

        searched_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            or_(
                Appointment.patient_id.in_(searched_patients_id),
                Appointment.date.contains(search_str),
                Appointment.public_id.ilike(search_str),
                Appointment.start_time.contains(search_str),
                Appointment.status.ilike(search_str)
            )
        ).all()

        if len(searched_appointments) == 0:
            abort(404, message="No Search Result Found.")

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
                if ap in searched_appointments:
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

            if len(appointments_data) == 0:
                return{ "message":"No Search Result Found."}, 404
            
            elif duration == "current-week":
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
            app.logger.exception(f"(Resource) DoctorSearchAppointments: (GET) (triggered) an error: {e}")
            abort(500, message="Appointments search data fetching failed.")

class PatientSearchUpcomingAppointments(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all upcoming appointments'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        searched_doctors_id = [-1]
        searched_doctors = Doctor.query.filter(
            or_(
                Doctor.full_name.contains(search_str),
                Doctor.public_id.ilike(search_str)
            )
        ).all()

        if len(searched_doctors) > 0:
            searched_doctors_id = [d.id for d in searched_doctors]

        searched_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            or_(
                Appointment.doctor_id.in_(searched_doctors_id),
                Appointment.date.contains(search_str),
                Appointment.public_id.ilike(search_str),
                Appointment.start_time.contains(search_str),
                Appointment.status.ilike(search_str.lower())
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
            ap = Appointment.query.filter_by(patient_id=patient.id,date=ap_date).all()
            appointments += ap

        try:
            appointments_data = []
            booked_appointments_data = []
            for ap in appointments:
                if ap in searched_appointments:
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
            app.logger.exception(f"(Resource) PatientSearchUpcomingAppointments: (triggered) an error: {e}")
            abort(500, message="Upcoming Appointments search data fetching failed.")

class PatientSearchDepartments(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective searched department details'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")


        searched_department = Department.query.filter(
            Department.name.contains(search_str)
        ).all()

        if len(searched_department) == 0:
            abort(404, message="No Search Result Found.")

        try:
            dept_data = []
            for d in searched_department:
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
            app.logger.exception(f"(Resource) PatientSearchDepartments: (triggered) an error: {e}")
            abort(500, message="Department search data fetching failed.")

class PatientSearchDepartmentDoctors(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective department filtered list of all available doctors data'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        # Searches for the department first
        try:
            department_query = non_empty_string(request.args.get("department"))
        except ValueError:
            abort(400, message="'department' parameter should not be empty.")

        searched_department = Department.query.filter(
                Department.name.contains(department_query)
        ).first()

        if not searched_department:
            abort(404, message="No Search Result Found.")

        # Searches for the department doctor
        try:
            doctor_query = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        searched_specialization = Specialization.query.filter(
            Specialization.name.contains(doctor_query)
        ).first()

        if not searched_specialization:
            searched_specialization_id = -1
        else:
            searched_specialization_id = searched_specialization.id
        
        searched_doctors = Doctor.query.filter(
            or_(
                Doctor.full_name.contains(doctor_query.title()),
                Doctor.public_id.ilike(doctor_query),
                Doctor.specialization_id.ilike(searched_specialization_id),
                Doctor.qualification.contains(doctor_query.upper())
            )
        ).all()

        if len(searched_doctors) == 0:
            abort(404, message="No Search Result Found.")

        dept_doctors_id = [d.doctor_id for d in (Departments_Doctors.query.filter_by(department_id=searched_department.id).all())]

        try:
            doctors_data = []
            
            for doc in searched_doctors:
                if doc.id in dept_doctors_id:
                    t = User.user_email(doc.user_id)
                    if t[1] == True: # if the doctor is active
                        doctors_data.append(
                            {
                                'doctor_public_id': doc.public_id,
                                'full_name': doc.full_name,
                                'department': searched_department.name,
                                'specialization': Specialization.spec_name(doc.specialization_id),
                                'qualification': doc.qualification,
                                'gender': doc.gender.title(),
                                'license': doc.license,
                                'experience': doc.experience,
                                'description': doc.description,
                            }
                        )

            if len(doctors_data) == 0:
                return{ "message":"No Search Result Found."}, 404
            else:
                return {
                    "count": len(doctors_data),
                    "department": searched_department.name,
                    "doctors": doctors_data
                }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientSearchDepartmentDoctors: (triggered) an error: {e}")
            abort(500, message="Upcoming Appointments search data fetching failed.")

class PatientSearchAppointmentHistory(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and response with the respective filtered list of all previous completed appointments history'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
             abort(404, message="Patient not found.")

        try:
            search_str = non_empty_string(request.args.get("query"))
        except ValueError:
            abort(400, message="'query' parameter should not be empty.")

        # Searches the doctors by their department in the appointment history
        searched_department = Department.query.filter(
            Department.name.contains(search_str)
        ).first()

        if searched_department:
            searched_dept_doctors = Departments_Doctors.query.filter_by(department_id=searched_department.id).all()
            searched_appointments = []
            for sdd in searched_dept_doctors:
                searched_appointments += Appointment.query.filter(
                    Appointment.patient_id == patient.id, 
                    Appointment.doctor_id == sdd.doctor_id
                ).all()
        else:
        # Searches the doctors and appointments by their public_id or date in the appointment history
            searched_doctors_id = [-1]
            searched_doctors = Doctor.query.filter(
                or_(
                    Doctor.full_name.contains(search_str),
                    Doctor.public_id.ilike(search_str)
                )
            ).all()

            if len(searched_doctors) > 0:
                searched_doctors_id = [d.id for d in searched_doctors]

            searched_appointments = Appointment.query.filter(
                Appointment.patient_id == patient.id, 

                or_(
                    Appointment.doctor_id.in_(searched_doctors_id),
                    Appointment.date.contains(search_str),
                    Appointment.public_id.ilike(search_str),
                    Appointment.start_time.contains(search_str),
                    Appointment.status.ilike(search_str)
                )
            ).all()

        if len(searched_appointments) == 0:
            abort(404, message="No Search Result Found.")

        try:
            pat_appointments_history = []

            for ap in searched_appointments:
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
                        'status': ap.status
                    }
                )

            if len(pat_appointments_history) == 0:
                return{ "message":"No Search Result Found."}, 404
            else:
                pat_appointments_history.reverse()
                return {
                    "count": len(pat_appointments_history),
                    "patient_public_id": patient.public_id,
                    "patient_full_name": patient.full_name,
                    "patient_history": pat_appointments_history
                }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientSearchAppointmentHistory: (triggered) an error: {e}")
            abort(500, message="Patient Appointment History search data fetching failed.")