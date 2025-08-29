from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DatabaseService import DatabaseService
from JedoxPy.Services.DimensionService import DimensionService
from JedoxPy.Services.ElementService import ElementService
from JedoxPy.Services.SubsetService import SubsetService
from JedoxPy.Services.CubeService import CubeService
from JedoxPy.Services.CellService import CellService
from JedoxPy.Services.RulesService import RulesService
from JedoxPy.Services.SupervisionServerService import SupervisionServerService
from JedoxPy.Services.SecurityService import SecurityService

class JedoxService:

    def __init__(self, **kwargs):
        self.connection = ConnectionService(**kwargs)

        # alias for connection service
        self.server = None
        self.databases = None
        self.cubes = None
        self.dimensions = None
        self.cells = None
        self.elements = None
        self.subsets = None
        self.svs = None
        self.rules = None
        self.security = None

    def connect(self):

        self.connection.connect()

        print(f"Connected to : {self.connection.host}. Print the connection object for more information")

        # alias for connection service
        self.server = self.connection
        self.databases = DatabaseService(self.connection)
        self.cubes = CubeService(self.connection)
        self.dimensions = DimensionService(self.connection)
        self.cells = CellService(self.connection)
        self.elements = ElementService(self.connection)
        self.subsets = SubsetService(self.connection)
        self.svs = SupervisionServerService(self.connection)
        self.rules = RulesService(self.connection)
        self.security = SecurityService(self.connection)

    def disconnect(self, sid=None):
        self.connection.disconnect(sid=sid)
        print(f"Disconnected from {self.connection.host}. See you next time!")


    def __enter__(self):
        self.connect()
        return self

    def __str__(self):
        return (f"Connected to : {self.connection.host} on port {self.connection.port} with session id {self.connection.session_id}, "
               f"user {self.connection.username}, {"locale " + self.connection.locale if self.connection.locale is not None else "default locale"}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


