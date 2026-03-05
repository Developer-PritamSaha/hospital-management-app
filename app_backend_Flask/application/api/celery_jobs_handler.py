from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from celery.result import AsyncResult

from app_backend_Flask.application import celery_tasks
from app_backend_Flask.application.models import *
from ..utils.input_validators import *

class ExportCsvReport(Resource):
    '''This resource consist of 'GET' & 'POST' method which checks 'access token' sent by the client and handles asynchronus csv export of the patient medical history'''

    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
            abort(404, message="Patient not found.")

        task_id = request.args.get("task_id")
        try:
            task_id = non_empty_string(task_id, "'task_id' parameter")
        except ValueError as e:
            abort(400, message=str(e))

        try:

            task = AsyncResult(task_id)

            if task.state == "SUCCESS":
                return {
                    "status": task.state.lower(),
                    "file_path": task.result["file_path"]
                }, 200
            elif task.state == "FAILED":
                return {
                    "status": task.state.lower(),
                }, 400
            else:
                return {
                    "status": task.state.lower(),
                }, 200

        except Exception as e:
            app.logger.exception(f"(Resource) ExportCsvReport: 'GET' (triggered) an error: {e}")
            abort(500, message="Export Csv Download Request failed.")

    @jwt_required()   
    def post(self):
        user_id = get_jwt_identity()
        
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        patient = Patient.query.filter_by(user_id=int(user_id)).first()
        if not patient:
            abort(404, message="Patient not found.")

        appoint_count = Appointment.query.filter_by(patient_id=patient.id, status='completed').count()

        if (appoint_count < 1):
            abort(404, message="No medical history available to be exported.")

        try:
            task = celery_tasks.generate_medical_history_csv.delay(patient.id, patient.public_id)
            return {
                "task_id": str(task.id),
                "message": "Medical History export started."
            }, 202
        
        except Exception as e:
            app.logger.exception(f"(Resource) ExportCsvReport: 'POST' (triggered) an error: {e}")
            abort(500, message="Export Csv Request failed.")