from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from app_backend_Flask.application.db_extensions import db
from app_backend_Flask.application.models import *
from app_backend_Flask.application.utils.input_validators import *

### Request Parser setup 
## For Doctor Data
deviceManageData_validator = reqparse.RequestParser()
deviceManageData_validator.add_argument("token_jti", type=non_empty_string, required=True, help="{error_msg}")


class UserDevices(Resource):
    '''This resource consist of only 'GET' method which checks 'access token' sent by the client and sent back all active devices for the user'''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            abort(401, message="User do not exist")
        
        accessToken_payload = get_jwt()
        currentRefreshToken_jti = accessToken_payload["refresh_jti"]

        try:
            active_devices = []
            refresh_tokens = User_Tokens.query.filter_by(user_id=int(user_id), type="refresh", valid=True).all()

            device_count = 0
            for rt in refresh_tokens:
                current_device = False
                if rt.is_valid():
                    device_count += 1

                    if rt.jti == currentRefreshToken_jti:
                        current_device = True

                    active_devices.append(
                        {
                            'device_name': f"Device {device_count}",
                            'token_jti': rt.jti,
                            'login_date': rt.create_datetime.strftime("%Y-%m-%d"),
                            'login_time': rt.create_datetime.strftime("%H:%M:%S"),
                            'current_device': current_device
                        }
                    )
                
            return {
                "count": len(active_devices),
                "devices": active_devices
            }, 200
            
        except Exception as e:
            app.logger.exception(f"(Resource) UserDevices: 'GET' (triggered) an error: {e}")
            abort(500, message="User loggedin devices fetching failed.")

class UserLogoutDevice(Resource):
    '''This resource consist of only 'POST' method which checks 'access token' sent by the client and handles device logout as per the request'''
    @jwt_required()   
    def post(self):
        if not request.is_json:
            abort(400, message="Only JSON data allowed")
        
        user_id = get_jwt_identity()
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            abort(401, message="User do not exist")
        
        args = deviceManageData_validator.parse_args()

        refreshToken_exist = User_Tokens.query.filter_by(jti=args['token_jti'], type='refresh').first()

        if not refreshToken_exist:
            abort(404, message="Device Token not exist")

        if not refreshToken_exist.is_valid():
            abort(400, message="Logout failed: Either device token is not valid or already revoked")

        activeAccessToken = User_Tokens.query.filter(
            User_Tokens.user_id == int(user_id),
            User_Tokens.parent_jti == args['token_jti'], 
            User_Tokens.type == 'access',
            User_Tokens.valid == True
        ).first()
        
        try:
            refreshToken_exist.valid = False
            activeAccessToken.valid = False
                
            db.session.flush()
            
        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Resource) UserLogoutDevice: (triggered) token invalidation commit rollback: (cause) {e}")
            abort(500, message="Device Logout Failed")
        else:
            db.session.commit()
            return {"message": "Logged out successfully"}, 200