import csv
from celery import shared_task
from flask_mail import Message
from flask import current_app as app
from flask import render_template
from datetime import datetime, timedelta
import calendar

from app_backend_Flask.application.extensions import db
from app_backend_Flask.application.models import *


@shared_task()
def reset_doctor_weekly_availability():
    '''Reassigns the new weekly dates for the existing availability schedules for the respective doctors'''
    current_datetime = datetime.now()
    weekday_index = int(current_datetime.strftime("%u")) - 1
    new_week_start_date = current_datetime.date() - timedelta(days=weekday_index)
    current_week_dates = [(new_week_start_date + timedelta(days=d)) for d in range(0,7)]

    try:
        availabilities = Availability.query.all()
        for a in availabilities:
            # Each day has three time slots
            if a.slot_id in ['d1s1', 'd1s2', 'd1s3']:
                a.date = current_week_dates[0] # For Monday
                a.appointments_count = 0
                db.session.flush()

            elif a.slot_id in ['d2s1', 'd2s2', 'd2s3']:
                a.date = current_week_dates[1] # For Tuesday
                a.appointments_count = 0
                db.session.flush()

            elif a.slot_id in ['d3s1', 'd3s2', 'd3s3']:
                a.date = current_week_dates[2] # For Wednesday
                a.appointments_count = 0
                db.session.flush()

            elif a.slot_id in ['d4s1', 'd4s2', 'd4s3']:
                a.date = current_week_dates[3] # For Thursday
                a.appointments_count = 0
                db.session.flush()

            elif a.slot_id in ['d5s1', 'd5s2', 'd5s3']:
                a.date = current_week_dates[4] # For Friday
                a.appointments_count = 0
                db.session.flush()

            elif a.slot_id in ['d6s1', 'd6s2', 'd6s3']:
                a.date = current_week_dates[5] # For Saturday
                a.appointments_count = 0
                db.session.flush()
            
            elif a.slot_id in ['d7s1', 'd7s2', 'd7s3']:
                a.date = current_week_dates[6] # For Sunday
                a.appointments_count = 0
                db.session.flush()

        new_notification = Notification(
            user_id = 1,
            date = datetime.now().date(),
            time = datetime.now().time(),
            data = 'All the doctors availability for the current week have been reassigned.',
            type = "info"
        )
        db.session.add(new_notification)
        db.session.flush()

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"(Celery_Task) reset_doctor_weekly_availability(): (triggered) doctor availability weekly reset update rollback (cause): {e}")
        return False
    else:
        db.session.commit()
        return True

@shared_task()
def cancel_pending_appointments(slot_end_time_str):
    '''Cancels the pending appointments after the time slot passes'''
    current_datetime = datetime.now()
    slot_end_time = datetime.strptime(slot_end_time_str, "%H:%M").time()
    try:
        appointments = Appointment.query.filter_by(
            date=current_datetime.date(),
            end_time=slot_end_time,
            status='booked'
        ).all()

        for ap in appointments:
            ap.status = 'canceled'
            db.session.flush()

        new_notification = Notification(
            user_id = 1,
            date = datetime.now().date(),
            time = datetime.now().time(),
            data = 'All the pending appointments are being auto canceled for the time slot.',
            type = "info"
        )
        db.session.add(new_notification)
        db.session.flush()

    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"(Celery_Task) cancel_pending_appointments(): (triggered) pending appointment cancel rollback (cause): {e}")
        return False
    else:
        db.session.commit()
        return True

@shared_task(bind=True)
def generate_medical_history_csv(self, pat_id, pat_pub_id):
    
    appointments_completed = Appointment.query.filter_by(patient_id=pat_id, status='completed').all()

    file_path = f"app_backend_Flask/exports/{pat_pub_id}_medical_history.csv"

    try:
        with open(file_path, "w", newline="") as file:
            write = csv.writer(file)

            write.writerow([
                "Date",
                "Time_Slot",
                "Appointment_Id",
                "Doctor_Name",
                "Doctor_Id",
                "Visit_Type",
                "Tests_Done",
                "Diagnosis",
                "Prescription",
                "Medicine",
                "Notes"
                
            ])

            for ap in appointments_completed:
                t = Treatment.query.filter_by(appointment_id=ap.id).first()
                ap_doc = Doctor.query.filter_by(id=ap.doctor_id).first()
                if t != None:
                    write.writerow([
                        ap.date.strftime("%Y-%m-%d"),
                        ap.start_time.strftime("%H:%M") + " to " + ap.end_time.strftime("%H:%M"),
                        ap.public_id,
                        ap_doc.full_name,
                        ap_doc.public_id,
                        t.visit_type,
                        t.test_done.replace("\n" , " and "),
                        t.diagnosis.replace("\n" , " and "),
                        t.prescription.replace("\n" , " and "),
                        t.medicine.replace("\n" , " and "),
                        t.notes.replace("\n" , " and ")
                    ])
        
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"(Celery_Task) generate_medical_history_csv(): (triggered) medical history export failed (cause): {e}")
        return {
            "message": "CSV Export Failed.",
            "file_path": "N/A"
        }
    
    else:
        return {
            "message": "CSV Export Started.",
            "file_path": file_path
        }
    
@shared_task()
def notify_patient_appointments():
    '''Notifies the upcoming appointments of the patients in their respective mail'''

    current_date = datetime.now().date()
    upcoming_appointments = Appointment.query.filter_by(date=current_date, status='booked').all()
    
    try:
        for ap in upcoming_appointments:
            # Add a notification to the users dashbaord
            pat = Patient.query.filter_by(id=ap.patient_id).first()
            doc = Doctor.query.filter_by(id=ap.doctor_id).first()
            if pat and doc:
                new_notification = Notification(
                    user_id = pat.user_id,
                    date = datetime.now().date(),
                    time = datetime.now().time(),
                    data = f'You have {doc.full_name} appointment on {ap.date.strftime("%d/%m/%y")} from {ap.start_time.strftime("%H:%M")} to {ap.end_time.strftime("%H:%M")}',
                    type = "info"
                )
                db.session.add(new_notification)
                db.session.flush()
            
                t = User.user_email(pat.user_id)
                msg = Message(
                    subject=f"Upcoming Appointment Reminder to {pat.full_name}",
                    recipients=[t[0]]
                )
                msg.body = f'''
                Hello {pat.full_name}, 
                    You have an upcoming appointment today from ({ap.start_time.strftime("%H:%M")} to {ap.end_time.strftime("%H:%M")}), to doctor {doc.full_name} specializes as {Specialization.spec_name(doc.specialization_id)}.
                    
                    Please try to visit within your selected time slot to not miss your appointment today. Thank You.'''
                
                app.extensions["mail"].send(msg)
                
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"(Celery_Task) notify_patient_appointments(): (triggered) booked upcoming appointment notification sending failed (cause): {e}")
        return False
    else:
        db.session.commit()
        return True
    
@shared_task()
def send_monthly_report():
    '''Sends the doctors monthly report summary'''

    now = datetime.now().date()
    month_start_date = now.replace(day=1)
    month_num_days = calendar.monthrange(now.year, now.month)[1]
    month_end_date = now.replace(day=month_num_days)

    month = {
        'start_date': month_start_date.strftime("%Y-%m-%d"),
        'end_date': month_end_date.strftime("%Y-%m-%d")
    }
    doctors = Doctor.query.all()
    
    try:
        for doc in doctors:
            doctor = {
                'pub_id': doc.public_id,
                'name': doc.full_name,
                'dept_name': Departments_Doctors.dept_name(doc.id)
            }

            appointments = []
            ap_datetime = {}
            patient = {}
            treatment = {}
        
            t = User.user_email(doc.user_id)
            msg = Message(
                subject=f"{doc.full_name}({doc.public_id}) Monthly Report",
                recipients=[t[0]]
            )
            msg.body = f'''
            Hello {doc.full_name}, 
                Please see the attached monthly report.'''
            
            # Data extraction for the report creation
            for day_num in range(1, month_num_days+1):
                ap_temps = Appointment.query.filter_by(doctor_id=doc.id,date=now.replace(day=day_num),status='completed').all()
                appointments += ap_temps
                for a in ap_temps:
                
                    ap_datetime[a.id] = {}
                    patient[a.id] = {}
                    treatment[a.id] = {}
                    
                    ap_datetime[a.id]['date'] = a.date.strftime("%Y-%m-%d")
                    ap_datetime[a.id]['start_time'] = a.start_time.strftime("%H:%M")
                    ap_datetime[a.id]['end_time'] = a.end_time.strftime("%H:%M")

                    pat = Patient.query.filter_by(id=a.patient_id).first()
                    if pat:
                        patient[a.id]['name'] = pat.full_name
                        patient[a.id]['pub_id'] = pat.public_id
                        patient[a.id]['gender'] = pat.gender.title()
                        patient[a.id]['age'] = now.year - pat.dob.year 
                    else:
                        patient[a.id]['name'] = 'Deleted'
                        patient[a.id]['pub_id'] = "n/a"
                        patient[a.id]['gender'] = 'n/a'
                        patient[a.id]['age'] = 'n/a'

                    treat = Treatment.query.filter_by(appointment_id=a.id).first()
                    if treat:
                        treatment[a.id]['visit_type'] = treat.visit_type
                        treatment[a.id]['test_done'] = treat.test_done
                        treatment[a.id]['diagnosis'] = treat.diagnosis
                        treatment[a.id]['medicine'] = treat.medicine
                        treatment[a.id]['prescription'] = treat.prescription
                        treatment[a.id]['notes'] = treat.notes
                        
                    else:
                        treatment[a.id]['visit_type'] = "n/a"
                        treatment[a.id]['test_done'] = "n/a"
                        treatment[a.id]['diagnosis'] = "n/a"
                        treatment[a.id]['medicine'] = "n/a"
                        treatment[a.id]['prescription'] = "n/a"
                        treatment[a.id]['notes'] = "n/a"

            msg.html = render_template("doc_monthly_report.html", month=month, doc=doctor, patient=patient, treatment=treatment, appointments=appointments, ap_datetime=ap_datetime)
            
            app.extensions["mail"].send(msg)

            # Send a notification to the doctors dashboard
            new_notification = Notification(
                user_id = doc.user_id,
                date = datetime.now().date(),
                time = datetime.now().time(),
                data = "Your Monthly Report has been sent to the respective e-mail, please check.",
                type = "info"
            )
            db.session.add(new_notification)
            db.session.flush()
                
    except Exception as e:
        db.session.rollback()
        app.logger.exception(f"(Celery_Task) send_monthly_report(): (triggered) monthly report sending failed (cause): {e}")
        return False
    else:
        db.session.commit()
        return True