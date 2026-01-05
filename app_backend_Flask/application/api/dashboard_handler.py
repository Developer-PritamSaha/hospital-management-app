from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import fields, marshal_with, abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from ..extensions import db
from app_backend_Flask.application.models import *

## Response field setup
# user_fields = {
#     "id": fields.Integer,
#     "username": fields.String,
#     "email": fields.String,
#     "role": fields.String
# }

# Dashboard handler API
class Dashboard(Resource):
    '''This resource consist of 'GET' method which checks 'access token' sent by the client and fulfill the requested operation by the client '''
    @jwt_required()   
    def get(self):
        user_id = get_jwt_identity()
        user_role = Roles_Users.user_role(int(user_id))
        if user_role in ["admin", "doctor", "patient"]:
            return {
                "msg": f"Welcome, to {user_role.upper()} dashboard"
            }, 200
        else:
            abort(401, message="Access denied.")

