from flask import request
from flask import current_app as app
from flask_restful import Resource, reqparse
from flask_restful import abort
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity, get_jwt
from datetime import datetime, timedelta

from app_backend_Flask.application import celery_tasks
from app_backend_Flask.application.models import *
from ..utils.input_validators import *

class TestJob(Resource):
    '''This resource consist of 'GET' & 'PATCH' method which checks 'access token' sent by the client and handles the appointments as per the request'''

    @jwt_required(optional=True)   
    def get(self):
        # user_id = get_jwt_identity()
        # if Roles_Users.user_role(int(user_id)) != "admin":
        #     abort(401, message="Admin Access needed.")

        args = request.args.get("args")
        try:
            args = non_empty_string(args, "'args' parameter")
        except ValueError as e:
            abort(400, message=str(e))


        try:
            job = celery_tasks.test_task.delay("Pritam")
            # job = "WTF"
            return {
                "job": str(job)
            }, 200
        
        except Exception as e:
            app.logger.exception(f"(Resource) TestJob: 'GET' (triggered) an error: {e}")
            abort(500, message="Job Request failed.")