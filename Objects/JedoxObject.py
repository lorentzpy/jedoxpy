from JedoxPy.Services.ConnectionService import ConnectionService

class JedoxObject:

    def __init__(self, name: str, type: int, id, connection):
        self._name = name
        self._type = type
        self._id = id
        self._connection = connection

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self):
        return self._id