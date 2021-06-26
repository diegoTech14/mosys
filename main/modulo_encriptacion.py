import bcrypt

def hashing_password(passw): # genera la contraseña hash y la une con la sal
    
    response = ""

    try:
        passw = passw.encode()
        salt = bcrypt.gensalt(rounds=16)
        hashed = bcrypt.hashpw(passw, salt)

        response = hashed.decode('utf-8')
        
    except TypeError:
            response = False
    
    finally:
        return response
        
def compare_password(new_password, password):

        new_password = new_password.encode()
        password = password.encode()
        
        try:
                if bcrypt.checkpw(new_password, password):
                        return 1
                else:
                        return 0
        except TypeError as e:
                print("Error de chequeo: ", e)