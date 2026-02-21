from email_validator import validate_email, EmailNotValidError 
from datetime import datetime
import string

## Custom Data Validation Functions
def non_empty_string(s,field_name=''):
    if (type(s) != str):
        raise ValueError(f"{field_name.title()} field must be string.")
    if s.strip() == '':
        raise ValueError(f"{field_name.title()} field can not be empty.")
    return str(s.strip())

def check_full_name(s):
    try:
        name_str = non_empty_string(s, "Full Name")
        full_name = name_str.split()
        joined_name = "".join(full_name)
        if(len(full_name) < 2):
            raise ValueError("Full Name must contain the name and title separated by a space.")
        elif(not joined_name.isalpha()):
            raise ValueError("Full Name must not contain any punctuations or numbers.")
        else:
            return(name_str)
    except ValueError as e:
        raise ValueError(e)

def check_gender(s):
    try:
        g = non_empty_string(s, "Gender")
        genders = ["male","female","trans"]
        if g.lower() not in genders:
            raise ValueError("Gender should be 'male', 'female', or 'trans'.")
        else:
            return(g.lower())
    except ValueError as e:
        raise ValueError(e)
    
def check_booking_status(s):
    try:
        sts = non_empty_string(s, "Status")
        statuses = ["booked","canceled","completed"]
        if sts.lower() not in statuses:
            raise ValueError("Status should be 'booked', 'canceled', or 'completed'.")
        else:
            return(sts.lower())
    except ValueError as e:
        raise ValueError(e)

def validate_passwd(passwd):
    try:
        password = str(passwd.strip())
        if len(password) < 8:
            raise ValueError("Password must contain 8 or more characters.")
        elif any(char in string.whitespace for char in password):
            raise ValueError("Password must not contain any whitespaces.")
        elif not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number.")
        elif not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        elif not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        elif not any(c in string.punctuation for c in password):
            raise ValueError("Password must contain at least one special character.")
        return password
    except AttributeError:
        raise ValueError("Password must be string.")
    except ValueError as e:
        raise ValueError(e)

def email_validator(email):
    try:
        non_empty_email = non_empty_string(email, "Email")
        validate_email(non_empty_email,check_deliverability=False) 
        return(non_empty_email.lower())
    except EmailNotValidError as e:
        raise ValueError(e)

def is_valid_contact(contact):
    try:
        contact_str = non_empty_string(contact, "Contact")
        if len(contact_str) != 10:
            raise ValueError("Contact must contain 10 digits.")
        elif not contact_str.isdigit():
            raise ValueError("Contact must contain only digits.")
        return(contact_str)
    except ValueError as e:
        raise ValueError(e)
    
def is_valid_date(date_string):
    """
    Checks if the given string is a valid date in 'yyyy-mm-dd' format as per ISO 8601.
    """
    try:
        date_str = non_empty_string(date_string, "Date")
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return(date)
    except ValueError as e:
        raise ValueError(e)

def is_valid_time(time_string):
    """
    Checks if the given string is a valid time in 'HH:MM' 24 hour format.
    """
    try:
        time_str = non_empty_string(time_string, "Time")
        time = datetime.strptime(time_str, '%H:%M').time()
        return(time)
    except ValueError as e:
        raise ValueError(e)

def is_integer(v, min_val=None, max_val=None):
    try:
        if isinstance(v, bool):
            raise ValueError("boolean is not an integer")

        if isinstance(v, str):
            if not v.strip().isdigit():
                raise ValueError("value should be an integer")
            v = int(v)

        if not isinstance(v, int):
            raise ValueError("value should be an integer")

        # Range check
        if min_val is not None and v < min_val:
            raise ValueError(f"value should be ≥ {min_val}")

        if max_val is not None and v > max_val:
            raise ValueError(f"value should be ≤ {max_val}")

        return(v)

    except ValueError as e:
        raise ValueError(e)