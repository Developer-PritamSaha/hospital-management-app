from email_validator import validate_email, EmailNotValidError 
from datetime import datetime
import string

## Custom Data Validation Functions
def non_empty_string(s):
    if (type(s) != str) or s.strip() == '':
        raise ValueError("Field can not empty.")
    return str(s.strip())

def check_gender(s):
    try:
        g = non_empty_string(s)
        genders = ["male","female","trans"]
        if g.lower() not in genders:
            raise ValueError("Value should be 'male', 'female', or 'trans'")
        else:
            return(g.lower())
    except ValueError as e:
        raise ValueError(e)

def validate_passwd(password):
    if len(password) < 8:
        raise ValueError("Password must contain 8 or more characters.")
    elif not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one number.")
    elif not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    elif not any(c.islower() for c in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    elif not any(c in string.punctuation for c in password):
        raise ValueError("Password must contain at least one special character.")
    return str(password.strip())

def email_validator(email):
    try:
        non_empty_email = non_empty_string(email)
        validate_email(non_empty_email,check_deliverability=False) 
        return(non_empty_email.lower())
    except EmailNotValidError as e:
        raise ValueError(e)
    
def is_valid_date(date_string):
    """
    Checks if the given string is a valid date in 'yyyy-mm-dd' format.
    """
    try:
        non_empty_string(date_string)
        date = datetime.strptime(date_string, '%Y-%m-%d').date()
        return(date)
    except ValueError as e:
        raise ValueError(e)

def is_integer(v,max:int=0,min:int=0):
    try:
        if not isinstance(v, int):
            raise ValueError("Value should be an integer.")
        if(max+min) > 0:
            if v < min or v > max: 
                raise ValueError(f"Value should be within({min} to {max}).")
        return(int(v))
    except ValueError as e:
        raise ValueError(e)