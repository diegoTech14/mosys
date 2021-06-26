
class configDatabase(object):

    def __init__(self, app):
        #__database_string = 'mysql+pymysql://diego:diegoduarteslipknot83@localhost/MOCIS'
        __database_string = 'mysql+pymysql://u7lbtrp6mz3yiwcf:PlaRN1hUxKcTbW0pzkvB@bceghupb0irwoqxvyocd-mysql.services.clever-cloud.com:3306/bceghupb0irwoqxvyocd'
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = __database_string
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
