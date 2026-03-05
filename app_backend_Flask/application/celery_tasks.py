import csv
from celery import shared_task
from flask import current_app as app
from datetime import datetime, timedelta

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
                print("From inside d1")

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
            writer = csv.writer(file)

            writer.writerow([
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
                    writer.writerow([
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