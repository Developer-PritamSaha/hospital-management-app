@jwt.unauthorized_loader # type: ignore
def missing_token_callback(e):
    return {
        "error": "Authorization required",
        "message": "Missing bearer authorization token in the header."
    }, 401

@jwt.expired_token_loader # type: ignore
def expired_token_callback(jwt_header, jwt_payload):
    return {
        "error": "Token Expired",
        'message': 'The authorization token has expired.'
    }, 403