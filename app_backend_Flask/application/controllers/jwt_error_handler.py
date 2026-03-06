from flask import current_app as app
from app_backend_Flask.application.models import *

# JWT error handlers
@app.extensions["jwt"].unauthorized_loader
def missing_token_callback(e):
    return {
        "error": "Authorization required",
        "message": "Missing bearer authorization token in the header."
    }, 401

@app.extensions["jwt"].expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    token_type = jwt_payload["type"]
    return {
        "error": "Token Expired",
        'message': f"The authorization {token_type} token has been expired."
    }, 403

@app.extensions["jwt"].invalid_token_loader
def invalid_token_callback(e):
   return {
        "error": "Invalid Token",
        'message': f"The authorization token has: {e}."
   }, 422

@app.extensions["jwt"].token_in_blocklist_loader
def check_token_validility(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = User_Tokens.query.filter_by(jti=jti).first()
    if (token == None) or not token.is_valid():
       return True
    else:
       return False

@app.extensions["jwt"].revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
   token_type = jwt_payload["type"]
   return{
      "error": "Token Revoked",
      "message": f"The authorization {token_type} token has been revoked.",
   }, 401