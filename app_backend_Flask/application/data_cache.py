from flask import current_app as app

from app_backend_Flask.application.models import *
from app_backend_Flask.application.utils.generate_credentials_uid import generate_uuid

@app.extensions["cache_data"].cached(timeout=300, key_prefix="patient_cache")
def get_all_patients():
    patients = Patient.query.all()
    return patients

@app.extensions["cache_data"].cached(timeout=600, key_prefix="doctor_cache")
def get_all_doctors():
    doctors = Doctor.query.all()
    return doctors

@app.extensions["cache_data"].memoize(6000)
def get_doctor_availability(doc_id):
    availabilities = Availability.query.filter_by(doctor_id=doc_id).all()
    return availabilities