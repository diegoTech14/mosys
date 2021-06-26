from flask import Flask, request, jsonify, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from modulo_encriptacion import hashing_password
from config_files.database_flask_config import configDatabase

application = Flask(__name__)
configDatabase(application)

marshmallow = Marshmallow(application)
db = SQLAlchemy(application)

#tipos de usuario

@application.route('/tiposUsuario/')
def get_type_of_users():

    import schemas
    import models

    all_type_of_users = db.session.query(models.TypeOfUsers).all()
    schema_type_of_users = schemas.type_of_users_schema.dump(all_type_of_users)

    return jsonify(schema_type_of_users)

@application.route('/tiposUsuario/<tipo>')
def get_type_of_user(tipo):

    import schemas
    import models
    
    response = None

    try:
        type_of_user = db.session.query(models.TypeOfUsers)\
        .filter_by(nombre_del_tipo=tipo).first()
        
        if type_of_user:
            response = schemas.type_of_user_schema.dump(type_of_user)
        else:
            response = {
            "message": "No se ha encontrado ningún tipo de usuario"
        }
    except:
        response = {"message": "Ha ocurrido un problema"}

    return jsonify(response)

@application.route('/tiposUsuario/', methods=['POST'])
def create_type_of_user():

    import models
    response = None

    try:
        name_of_type = request.json['tipo_de_usuario']
        new_type_of_user = models.TypeOfUsers(nombre_del_tipo=name_of_type)
        db.session.add(new_type_of_user)
        db.session.commit()

        response = {"message":"Tipo de usuario registrado con éxito"}
    except:
        response = {"message":"Ha ocurrido un problema al intentar registrar"}
    
    return jsonify(response)

@application.route('/tiposUsuario/<id>', methods=['PUT'])
def update_type_of_user(id):
    
    import models
    response = None

    try:
        type_of_user = db.session.query(models.TypeOfUsers).get(int(id))
        
        if type_of_user:
            type_of_user.nombre_del_tipo = request.json['tipo_de_usuario']
            response = {"message": "Tipo de usuario actualizado"}
            db.session.add(type_of_user)
            db.session.commit()
    
        else:
            response = {"message": "No se ha encontrado tipo de usuario"}
    except:
        response = {"message": "Ha ocurrido un problema"}

    finally:
        return jsonify(response)

@application.route('/tiposUsuario/<id>', methods=['DELETE'])
def delete_type_of_user(id):
    
    import models 
    response = None
    
    try:
        type_of_user = db.session.query(models.TypeOfUsers).get(id)

        if type_of_user:
            
            db.session.delete(type_of_user)
            db.session.commit()

            response = {"message": "Tipo de usuario eliminado"}
        else:
            response = {"message": "No se ha encontrado tipo de usuario"}

    except:
        response = {"message": "Ha ocurrido un problema"}

    finally: 
        return jsonify(response)
        
#usuarios
        
@application.route('/usuarios/')
def get_users():

    import schemas
    import models

    response = None
    
    try:
        all_users = db.session.query(models.Users, models.TypeOfUsers)\
        .join(
            models.Users, 
            models.Users.tipo_de_usuario_foreign==models.TypeOfUsers.tipo_de_usuario_pkey
        )
    
        if all_users:
            users_dict = {}
            counter = 0

            for user in all_users:
        
                counter += 1
                users_dict['user {}'.format(counter)] = schemas.users_schema.dump(user)
        
            response = users_dict
        else:
            response = {
                "message": "No existen usuarios"
            }
    except:
        response = {
            "message": "Ha ocurrido un problema"
        }
    finally:
        return jsonify(response)

@application.route('/usuarios/<dni>')
def get_user(dni):

    import models
    import schemas

    response = None

    try:

        search_user = db.session.query(models.Users, models.TypeOfUsers)\
        .filter_by(usuario_cedula_pkey=dni)\
        .join(
            models.Users, 
            models.Users.tipo_de_usuario_foreign==models.TypeOfUsers.tipo_de_usuario_pkey
        ).first()

        if search_user:
            response = schemas.users_schema.dump(search_user)
        else:
            response = {
                "message": "No se ha encontrado el usuario"
            }
    except:
        response = {
            "message": "Ha ocurrido un problema"
        }

    finally:
        return jsonify(response)

@application.route('/usuarios/', methods=['POST'])
def create_user():

    import models
    response = None

    try:
        
        if hashing_password(request.json['contrasena']):

            data_new_user = {
                "usuario_cedula_pkey": request.json['cedula'],
                "nombre": request.json['nombre'],
                "apellido_paterno": request.json['apellido_paterno'],
                "apellido_materno": request.json['apellido_materno'],
                "correo": request.json['correo'],
                "telefono": request.json['telefono'],
                "contraseña": hashing_password(request.json['contrasena']),
                "estado": int(request.json['estado']),
                "tipo_de_usuario_foreign": int(request.json['tipo_de_usuario'])
            }
        
            new_user = models.Users(**data_new_user)

            db.session.add(new_user)
            db.session.commit()

            response = {"message": "Usuario creado"}
        
        else:
            raise Exception("")

    except Exception as error:
        print(error)
        response = {"message": "Ha ocurrido un problema"}

    finally:
        return jsonify(response)

@application.route('/usuarios/<dni>', methods=['PUT'])
def update_user(dni):

    import models
    import schemas

    response = None

    try:
        user = db.session.query(models.Users).get(dni)
        if user:
            
            user.nombre = request.json['nombre']
            user.apellido_paterno = request.json['apellido_paterno']
            user.apellido_materno = request.json['apellido_materno']
            user.correo = request.json['correo']
            user.telefono = request.json['telefono']
            user.contraseña = request.json['contrasena']
            user.estado = int(request.json['estado'])

            db.session.add(user)
            db.session.commit()

            response = {
                "message": "Usuario actualizado"
            }
        else:
            response = {
                "message": "No se ha encontrado ningun usuario"
            }
    except:
        response = {
            "message": "Ha ocurrido un problema"
        }
    finally:
        return jsonify(response)

@application.route('/usuarios/<dni>', methods=['DELETE'])
def delete_user(dni):

    import models
    response = None

    try:
        user = db.session.query(models.Users).get(dni)
        if user:

            db.session.delete(user)
            db.session.commit()

            response = {
                "message": "Usuario eliminado"
            }
        else:
            response = {
                "message": "Usuario no encontrado"
            }
    except: 
        response = {
            "message": "Ha ocurrido un problema"
        }
            
    finally:
        return jsonify(response)

#direcciones 

@application.route('/direcciones/')
def get_directions():

    import schemas
    import models
    response = None

    try:
        all_directions = models.Directions.query.all()
        
        if all_directions:
            response = schemas.directions_schema.dump(all_directions)
        else:
            response = {"message": "No hay direcciones"}
    except:
        response = {"message": "Ha ocurrido un problema"}
    finally:
        return jsonify(response)

@application.route('/direcciones/<id>')
def get_direction(id):

    import schemas 
    import models
    response = None

    try:
        direction = db.session.query(models.Directions).get(id)

        if direction:
            schema_direction = schemas.direction_schema.dump(direction)
            response = schema_direction
        else:
            response = {"message": "No se ha encontrado direccion"}
    except: 
        response = {"message": "Ha ocurrido un problema"}

    finally:
        return jsonify(response)

@application.route('/direcciones/', methods=['POST'])
def create_direction():
    
    import models
    
    response = None
    
    try:
        data_direction = {
            "ciudad": request.json['ciudad'],
            "barrio": request.json['barrio'],
            "direccion": request.json['direccion']
        }
  
        new_direction = models.Directions(**data_direction)
        
        db.session.add(new_direction)
        db.session.commit()
        
        response = {
            "message": "Direccion registrada"
        }
        
    except Exception as error:
        print(error)
        response = {
            "message": "Ha ocurrido un problema en el registro"
        }
    finally:
        return jsonify(response)
    
@application.route('/direcciones/<id>', methods=['PUT'])
def update_direction(id): 
    
    import models
    response = None
    
    direction_data = {
        "ciudad": request.json['ciudad'],
        "barrio": request.json['barrio'],
        "direccion": request.json['direccion']
    }
    
    try:
        direction = db.session.query(models.Directions).get(id)
        
        if direction:
            
            direction.ciudad = direction_data['ciudad']
            direction.barrio = direction_data['barrio']
            direction.direccion = direction_data['direccion']
            
            db.session.add(direction)
            db.session.commit()
            
            response = {
                "message": "direccion actualizada"
            }
        else:
            response = {
                "message": "No se ha encontrado direccion"
            }
    except Exception as error:
        
        print(error)
       
        response = {
            "message": "Ha ocurrido un problema"
        }
        
    finally:
        return jsonify(response)
        
# egresos
    
@application.route('/egresos/')
def get_expenses():
    
    import models
    import schemas
    
    response = None
    
    try:
        expenses = db.session.query(models.Expenses).all()
    
        if expenses:
            
            expenses_schema = schemas.expenses_schema.dump(expenses)
            
            for expense in expenses_schema:
                expense['peso'] = round(expense['peso'], 2)
            
            response = expense
            
        else:
            response = {
                "message": "No hay egresos"
            }
    except:
        response = {
            "message": "Ha ocurrido un problema"
        }
        
    finally:
        return jsonify(response)

@application.route('/egresos/', methods=['POST'])
def create_expense():
    
    import models
    response = None
    
    data_expense = {
        "fecha_egreso": request.json['fecha_egreso'],
        "material": request.json['material'],
        "cantidad": request.json['cantidad'],
        "proveedor": request.json['proveedor'],
        "costo": request.json['costo'],
        "peso": request.json['peso']
    }
    
    try:
        new_expense = models.Expenses(**data_expense)
        db.session.add(new_expense)
        db.session.commit()
        
        response = {
            "message": "Se ha registrado el ingreso"
        }
        
    except:
        response = {
            "message": "Ha ocurrido un problema"
        }
        
    finally:
        return jsonify(response)

@application.route('/egresos/<id>', methods=['PUT'])
def update_expense(id):
    
    import models
    import schemas
    
    response = None
    
    try:
        
        egreso = db.session.query(models.Expenses).get(id)
        
        if egreso:
            
            data_expense_update = {
                "fecha_egreso": request.json['fecha_egreso'],
                "material": request.json['material'],
                "cantidad": request.json['cantidad'],
                "proveedor": request.json['proveedor'],
                "costo": request.json['costo'],
                "peso": request.json['peso']
            } 
        
            egreso.fecha_egreso = data_expense_update['fecha_egreso']
            egreso.material = data_expense_update['material']
            egreso.cantidad = data_expense_update['cantidad']
            egreso.proveedor = data_expense_update['proveedor']
            egreso.costo = data_expense_update['costo']
            egreso.peso = data_expense_update['peso']
        
            db.session.add(egreso)
            db.session.commit()
        
            response = {
                "message": "Datos actualizados"
            }
            
        else:
            response = {
                "message": "No se ha encontrado egreso"
            }
    except:
    
        response = {
            "message": "Ha ocurrido un problema"
        }
        
    finally:
        return jsonify(response)

@application.route('/egresos/<id>', methods=['DELETE'])
def delete_expense(id):
    
    import models
    response = None
    
    try:
        egreso = db.session.query(models.Expenses).get(id)
        
        if egreso:
            
            db.session.delete(egreso)
            db.session.commit()
            
            response = {
                "message": "Egreso eliminado"
            }
            
        else:
            response = {
                "message": "Egreso no encontrado"
            }
    except:
            response = {
                "message": "Egreso eliminado"
            }
    finally:
        return response

# clientes

@application.route('/clientes/', methods=['POST'])
def create_client():
    
    import models 
    import schemas
    
    response = None
    
    data_client = {
        "nombre": request.json['nombre'],
        "apellido": request.json['apellido'],
        "telefono": request.json['telefono'],
        "direccion_id_foreign": request.json['direccion_id']
    }
    
    try:
        
        new_client = models.Clients(**data_client)
        db.session.add(new_client)
        db.session.commit()
        
        response = {
            "message": "Cliente creado correctamente"
        }
    
    except:
        
        response = {
            "message": "Ha ocurrido un problema"
        }
    
    finally:
        
        return jsonify(response)
        
@application.route('/clientes/<id>')
def get_client(id):

    import schemas
    import models
    
    response = None

    try:
        client = db.session.query(models.Clients, models.Directions)\
        .filter_by(cliente_id_pkey=id)\
        .join(
            models.Clients,
            models.Clients.direccion_id_foreign==models.Directions.direccion_id_pkey
        ).first()

        if client:
            
            response = schemas.clients_schema.dump(client)

        else:
            response = {
                "message": "No hay clientes registrados"
            }
        
    except Exception as error:
        print(error)
        response = {
            "message": "Ha ocurrido un problema"
        }
    
    finally:
        return jsonify(response)

@application.route('/clientes/<id>', methods=['DELETE'])
def delete_client(id):

    import models
    response = None
    
    try:
        client = db.session.query(models.Clients).get(id)
        
        if client:
            
            db.session.delete(client)
            db.session.commit()
            
            response = {"message": "Cliente eliminado"}
            
        else:
            response = {"message": "Cliente no encontrado"}
    
    except:
            response = {"message": "Ha ocurrido un problema"}
    
    finally:
        return response

@application.route('/clientes/<id>', methods=['PUT'])
def update_client(id):

    import models   
    import schemas

    response = None

    try:
        data_update = {
            "nombre": request.json['nombre'],
            "apellido": request.json['apellido'],
            "telefono": request.json['telefono']
        }

        client = db.session.query(models.Clients).get(id)
        
        if client:
            client.nombre = data_update['nombre']
            client.apellido = data_update['apellido']
            client.telefono = data_update['telefono']
            db.session.add(client)
            db.session.commit()

            response = {
                "message": "Cliente actualizado"
            }
            
        else:
            response = {
                "message": "Cliente no encontrado"
            }

    except Exception as error:
        print(error)
        response = {
            "message": "Ha ocurrido un problema"
        }

    finally:
        return jsonify(response)


#Pedidos

@application.route('/pedidos/')
def get_orders():

    import schemas
    import models


    all_orders = db.session.query(models.Orders, models.TypesOfDelivery)\
    .join(
        models.Orders,
        models.Orders.tipo_de_entrega==models.TypeOfUsers.tipo_de_usuario_pkey
    )
    
    schema_all_orders = schemas.orders_schema.dump(all_orders)
    
    return jsonify(schema_all_orders)

@application.route('/pedidos/', methods=['POST'])
def create_orders():
    
    import models
    import schemas
    
    response = None
    
    data_order = {
        "estado": request.json['estado'],
        "fecha": request.json['fecha'],
        "metodo_de_pago": request.json['metodo_de_pago'],
        "tipo_de_entrega": request.json['tipo_de_entrega']
    }
    
    try:
        new_order = models.Orders(**data_order)
        db.session.add(new_order)
        db.session.commit()
        
        response = {
            "message": "Orden realizada correctamente"
        }
        
    except Exception as error:
        print(error)
        response = {
            "message": "Ha ocurrido un problema"
        }
        
    finally:
    
        return jsonify(response)
    
@application.route('/pedidos/<id>', methods=['PUT'])
def disable_order(id):
            
    import models
    response = None
    
    try:
        order = db.session.query(models.Orders).get(id)
        
        order_data_update = {
            "status": request.json['estado']
        }
        
        if order:
        
            order.estado = order_data_update['status']
            db.session.add(order)
            db.session.commit()

            response = {"message": "Orden deshecha"}
            
        else:
            response = {"message": "Orden no encontrada"}
    except:
            response = {"message": "Ha ocurrido un problema"}

    finally:
        return jsonify(response)

@application.route('/pedidos/<id>', methods=['PUT'])
def update_order(id):

    import models
    response = None

    try:
        order = db.session.query(models.Orders).get(id)

        order_data_update = {
            "status": request.json['estado'],
            "date": request.json['fecha'],
            "method_of_pay": request.json['metodo_de_pago'],
            "delivery_type": request.json['tipo_de_entrega']
        }

        if order:

            order.estado = order_data_update['status']
            order.fecha = order_data_update['date']
            order.metodo_de_pago = order_data_update['method_of_pay']
            order.tipo_de_entrega = order_data_update['delivery_type']
            db.session.add(order)
            db.session.commit()

            response = {"message": "Orden actualizada"}

        else:
            response = {"message": "Orden no encontrada"}

    except:
        response = {"message": "Ha ocurrido un problema"}

    finally:
        return jsonify(response)

#productos

@application.route('/productos/')
def all_products():

    import schemas
    import models

    all_products = models.Products.query.all()
    schema_all_products = schemas.products_schema.dump(all_products)

    return jsonify(schema_all_products)

@application.route('/productos/', methods=['POST'])
def create_product():

    import models
    import schemas
    
    response = None

    new_product_data = {
        "nombre": request.json['nombre'],
        "siglas": request.json['siglas'],
        "precio": request.json['precio']
    }

    try:
        
        new_product = models.Products(**new_product_data)
        db.session.add(new_product)
        db.session.commit()

        response = {"message": "Producto creado correctamente"}
    
    except Exception as error:
        print(error)
        response = {"message": "Ha ocurrido un problema"}
    
    finally: 
        
        return jsonify(response)

@application.route('/productos/<id>', methods=['DELETE'])
def delete_product(id):
    
    import models 
    response = ""

    try:
        producto = db.session.query(models.Products).get(id)

        if producto:

            db.session.delete(producto)
            db.session.commit()

            response = {"message": "Producto eliminado"}
        
        else:
            response = {"message": "No se ha encontrado el producto"}
    
    except:
        response = {"message": "Ha ocurrido un problema"}
    
    finally:
        return jsonify(response)

@application.route('/productos<id>/', methods=['PUT'])
def update_product(id):

    import models 
    response = ""
    
    update_product_data = {
        "nombre": request.json['nombre'],
        "siglas": request.json['siglas'],
        "precio": request.json['precio']
    }

    try:
        producto = db.session.query(models.Products).get(id)

        if producto:

            producto.nombre = update_product_data['nombre']
            producto.siglas = update_product_data['siglas']
            producto.precio = update_product_data['precio']

            db.session.add(producto)
            db.session.commit()

            response = {"message": "El producto se ha actualizado correctamente"}

        else:
            response = {"message": "No se ha encontrado el producto"}

    except:
        response = {"message": "Ha ocurrido un problema"}

    finally:

        return jsonify(response)

# tipos de entrega

@application.route('/tiposEntrega/')
def all_delivery_type():

    import schemas
    import models

    all_types_of_delivery = models.TypesOfDelivery.query.all()
    schema_all_types_of_delivery = schemas.types_of_delivery_schema.dump(all_types_of_delivery)
    
    return jsonify(schema_all_types_of_delivery)

@application.route('/tiposEntrega/', methods=['POST'])
def create_delivery_type():
    
    import schemas
    import models
    
    data_delivery_type = {
        "tipo_de_entrega": request.json["tipo_de_entrega"],
        "costo_adicional": request.json["costo_adicional"]
    }
    
    try:
        
        new_delivery_type = models.TypesOfDelivery(**data_delivery_type)
        
        db.session.add(new_delivery_type)
        db.session.commit()
    
        response = {
            "message": "Tipo de entrega registrado correctamente"
        }
        
    except Exception as error:
        print(error)
        response = {
            "message": "Ha ocurrido un problema"
        }
    
    finally:
        
        return jsonify(response)

@application.route('/tiposEntrega/<id>', methods=['DELETE'])
def delete_delivery_type(id):
    
    import models
    response = ""

    try:
        delivery_type = db.session.query(models.TypesOfDelivery).get(id)

        if delivery_type:
            
            db.session.delete(delivery_type)
            db.session.commit()

            response = {"message": "Tipo de entrega eliminado"}

        else:        
            response = {"message": "Tipo de entrega no encontrado"}
    
    except:
        response = {"message": "Ha ocurrido un problema"}
    
    finally:
        return jsonify(response)

@application.route('/tiposEntrega/<id>', methods=['PUT'])
def update_delivery_type(id):

    import models
    response = ""

    try:
        delivery_type = db.session.query(models.TypesOfDelivery).get(1)
    
        data_delivery_type_update = {
            "delivery_type": request.json['tipo_de_entrega'],
            "aditional_cost": request.json['costo_adicional']
        }
    
        if delivery_type:

            delivery_type.tipo_de_entrega = data_delivery_type_update['delivery_type']
            delivery_type.costo_adicional = data_delivery_type_update['aditional_cost']

            db.session.add(delivery_type)
            db.session.commit()
    
            response = {"message": "Tipo de entrega actualizado"}

        else:
            response = {"message": "No se ha encontrado tipo de entrega"}
    except Exception as error:
        print(error)
        response = {"message": "Ha ocurrido un problema"}
    
    finally:

        return jsonify(response)

if __name__ == '__main__':
    application.run(debug=True)
