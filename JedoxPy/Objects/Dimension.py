from JedoxPy.Objects.JedoxObject import JedoxObject
from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Enums import TypeObject, DimensionType

class Dimension:

    def __init__(self, name: str, type: int = None, id = None, number_elements = None):

        #super().__init__(name, type, id, connection)
        self.name = name
        self.id = id if id is not None else None
        self.type = DimensionType(int(type)) if type is not None else None
        self.number_elements = int(number_elements) if number_elements is not None else None
        self.virtual_attributes = None

    def __str__(self):
        type_name = self.type.name if self.type else "None"
        return (f"Object {self.__class__.__name__}. "
                f"Database {self.database.name}. "
                f"Name: {self.name} ; "
                f"Id: {self.id} ; "
                f"Type: {type_name} ; "
                f"Number of elements: {self.number_elements} ; "
                f"Attributes: {self.attributes} ;"
                f"Virtual attributes: {self.virtual_attributes}"
                )

    def __repr__(self):
        pass

    @classmethod
    def from_dict(cls, dimension_as_dict) -> 'Dimension':
        #obj = super().from_dict(cube_as_dict, key_name="name_cube", key_id="cube")
        name = dimension_as_dict.get("name_dimension")
        type_ = dimension_as_dict.get("type")
        id = dimension_as_dict.get("dimension")
        number_elements = dimension_as_dict.get("number_elements")
        #cls.connection = connection

        return cls(name=name, type=type_, id=id, number_elements=number_elements)

    def exists(self):

        connection_s = ConnectionService()

        return connection_s.get_version()

    def set_database(cls, database: Database):

        cls.database = database

    def set_attributes(cls, attributes):

        cls.attributes = attributes

    def set_virtual_attributes(cls, virtual_attributes):

        cls.virtual_attributes = virtual_attributes