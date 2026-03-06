from flask import request
from flask import current_app as app
from flask_restful import Resource
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from ..extensions import db
from app_backend_Flask.application.models import Notification, Roles_Users
from ..utils.input_validators import is_integer

class AdminNotifications(Resource):
    '''This resource consist of 'GET' & 'DELETE' method which checks 'access token' sent by the client and handles the patient notifications'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")

        notifications = Notification.query.filter_by(user_id=int(user_id)).all()

        try:
            notify_data = []
            for n in notifications:
                notify_data.append(
                    {
                        'id': n.id,
                        'date': n.date.strftime("%d/%m/%y"),
                        'time': n.time.strftime("%H:%M"),
                        'data': n.data,
                        'type': n.type
                    }
                )
                
            notify_data.reverse()
            return {
                "count": len(notify_data),
                "notifications": notify_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) AdminNotifications: (GET) (triggered) an error: {e}")
            abort(500, message="Admin notification data fetching failed.")
        
    @jwt_required()   
    def delete(self):
        
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "admin":
            abort(401, message="Admin Access needed.")
        
        notify_id = request.args.get("notification_id")
        try:
            notify_id = is_integer(notify_id)
        except ValueError:
            abort(400, message="'notification_id' parameter should be an integer and not empty.")

        notification = Notification.query.filter_by(id=notify_id, user_id=int(user_id)).first()
        if not notification:
             abort(404, message="Notification donot exist.")

        try:
            db.session.delete(notification)
            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) AdminNotifications: 'DELETE' (triggered) an error: {e}")
            abort(500, message="Admin Notification deletion failed.")
        else:
            db.session.commit()
            return {"message": "Notification deleted successfully."}, 200 

class DoctorNotifications(Resource):
    '''This resource consist of 'GET' & 'DELETE' method which checks 'access token' sent by the client and handles the doctor notifications'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")

        notifications = Notification.query.filter_by(user_id=int(user_id)).all()

        try:
            notify_data = []
            for n in notifications:
                notify_data.append(
                    {
                        'id': n.id,
                        'date': n.date.strftime("%d/%m/%y"),
                        'time': n.time.strftime("%H:%M"),
                        'data': n.data,
                        'type': n.type
                    }
                )
                
            notify_data.reverse()
            return {
                "count": len(notify_data),
                "notifications": notify_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) DoctorNotifications: (GET) (triggered) an error: {e}")
            abort(500, message="Doctor notification data fetching failed.")
    
    @jwt_required()   
    def delete(self):
        
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "doctor":
            abort(401, message="Doctor Access needed.")
        
        notify_id = request.args.get("notification_id")
        try:
            notify_id = is_integer(notify_id)
        except ValueError:
            abort(400, message="'notification_id' parameter should be an integer and not empty.")

        notification = Notification.query.filter_by(id=notify_id, user_id=int(user_id)).first()
        if not notification:
             abort(404, message="Notification donot exist.")

        try:
            db.session.delete(notification)
            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) DoctorNotifications: 'DELETE' (triggered) an error: {e}")
            abort(500, message="Doctor Notification deletion failed.")
        else:
            db.session.commit()
            return {"message": "Notification deleted successfully."}, 200 

class PatientNotifications(Resource):
    '''This resource consist of 'GET' & 'DELETE' method which checks 'access token' sent by the client and handles the patient notifications'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")

        notifications = Notification.query.filter_by(user_id=int(user_id)).all()

        try:
            notify_data = []
            for n in notifications:
                notify_data.append(
                    {
                        'id': n.id,
                        'date': n.date.strftime("%d/%m/%y"),
                        'time': n.time.strftime("%H:%M"),
                        'data': n.data,
                        'type': n.type
                    }
                )
                
            notify_data.reverse()
            return {
                "count": len(notify_data),
                "notifications": notify_data
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) PatientNotifications: (GET) (triggered) an error: {e}")
            abort(500, message="Patient notification data fetching failed.")

    @jwt_required()   
    def delete(self):
        
        user_id = get_jwt_identity()
        if Roles_Users.user_role(int(user_id)) != "patient":
            abort(401, message="Patient Access needed.")
        
        notify_id = request.args.get("notification_id")
        try:
            notify_id = is_integer(notify_id)
        except ValueError:
            abort(400, message="'notification_id' parameter should be an integer and not empty.")

        notification = Notification.query.filter_by(id=notify_id, user_id=int(user_id)).first()
        if not notification:
             abort(404, message="Notification donot exist.")

        try:
            db.session.delete(notification)
            db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) PatientNotifications: 'DELETE' (triggered) an error: {e}")
            abort(500, message="Patient Notification deletion failed.")
        else:
            db.session.commit()
            return {"message": "Notification deleted successfully."}, 200 