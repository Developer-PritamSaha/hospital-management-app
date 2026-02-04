import secrets, string
import uuid

def generate_uuid(prefix:str="", length:int=8) -> str:
    """
    Generates a n-length hexadecimal uuid

        :param str prefix: the string to be attached before the code (default "")
        :param int length: the length of the uuid (default 8)
        :return: the generated n-length uuid
        :rtype: str
    """
    return f"{prefix}{uuid.uuid4().hex[:length].upper()}"

def generate_password(passwd_len:int=8) -> str:
    """
    Generates Cryptographically secure n-length password

        :param int passwd_len: the length of the password (default 8)
        :return: the randomly generated n-length password
        :rtype: str
        :raises ValueError: if the password length < 8
    """
    if passwd_len < 8:
        raise ValueError("Password length should be at least 8.")
    
    punctuations = "!@#$%^&*+"
    passwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(punctuations)
    ]
    
    chars = string.ascii_letters + string.digits + punctuations
    passwd += [secrets.choice(chars) for _ in range(passwd_len - 4)]

    secrets.SystemRandom().shuffle(passwd)
    shuffled_passwd = "".join(passwd)
    return(secrets.choice("123456789")+shuffled_passwd)

def generate_id(user:str="admin",domain:str="@example.com",rand_code_len:int=6) -> str:
    """
    Generates Cryptographically secure user id
        -- Format: user + '.' + rand_code + domain

        :param user str: the user role (default "admin")
        :param domain str: the access level (default "@example.com")
        :param rand_code_len int: the randomized code length (default 6)
        :return: the generated user email
        :rtype: str
        :raises ValueError: if the random code length < 6

    """
    if rand_code_len < 6:
        raise ValueError("Random code length should be at least 6.")
    
    # rand_code = [secrets.choice(string.digits),secrets.choice(string.digits)]
    # rand_code += [secrets.choice(string.ascii_lowercase) for _ in range(rand_code_len - 2)]

    # secrets.SystemRandom().shuffle(rand_code)
    # rand_code = "".join(rand_code)
    rand_code = generate_uuid("",6)
    return ((user+'.'+rand_code+domain).lower())

def save_credentials(email:str="N/A", password:str="N/A", file_path:str="./undefined_cred.txt", type:str="Undefined") -> None:
    """
    Saves the provided email and password and if the provided file_path already exist it overwrites the content with the new credentials

        :param email str: the email id (default "N/A")
        :param password str: the access level (default "N/A")
        :param file_path str: the location to store the credential (default "./undefined_cred.txt")
        :param type str: the type of credential (default "Undefined")
        :return: None
        :raises Exception: if the credential file fails to save or write
    """
    try:
        with open(file_path, "w") as f:
            f.write(f">> HMS {type} Credentials\n")
            f.write(f"**Note: This file contains the {type} credentials for the HMS application. Do not share this file.\n\n") 

            f.write(f"{type} Email: {email}\n")
            f.write(f"{type} Password: {password}\n\n")
    except FileNotFoundError:
        raise FileNotFoundError("The directory for the file was not found.")
    except PermissionError:
        raise PermissionError("Provided file path donot have write permission.")
    except OSError as e:
        raise OSError(f"An OS error occurred: {e}")
    except TypeError as e:
        raise TypeError(f"Non string data can not be used for writing: {e}")
    except Exception as e:
        raise Exception(f"Some error occured during saving the {type} credentials: {e}")