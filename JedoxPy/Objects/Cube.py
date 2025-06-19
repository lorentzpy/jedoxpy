from JedoxPy.Objects.JedoxObject import JedoxObject
from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Objects.Enums import TypeObject
from JedoxPy.Objects.Database import Database

class Cube:

    def __init__(self, name: str, type: int=None, id: int=None, dimensions: list=None, number_cells: int=None, number_filled_cells: int=None):

        self.name = name
        self.id = id if id is not None else None
        self._type = TypeObject(type) if type is not None else None
        self.dimensions = dimensions if dimensions is not None else None
        self.number_cells = number_cells if number_cells is not None else None
        self.number_filled_cells = number_filled_cells if number_filled_cells is not None else None
        self.database = None
        self.number_of_rules = None

    def __str__(self):

        type_name = self._type.name if self._type else "None"
        return (f"Object {self.__class__.__name__} in database {self.database.name} (id {self.database.id})."
                f"Name: {self.name} ; "
                f"Id: {self.id} ; "
                f"Type: {type_name} ; "
                f"Dimensions: {self.dimensions} ; "
                f"Number of cells: {self.number_cells} ; "
                f"Number of filled cells: {self.number_filled_cells} ; "
                f"Number of rules: {self.number_of_rules}"
                )

    def __repr__(self):

        type_name = self._type.name if self._type else "None"
        return (f"Cube(name={self.name},"
                f"id={self.id},"
                f"dimensions={self.dimensions})"
                )

    @classmethod
    def from_dict(cls, cube_as_dict: dict) -> 'Cube':

        name = cube_as_dict.get("name_cube")
        type_ = cube_as_dict.get("type")
        id = cube_as_dict.get("cube")
        dimensions = cube_as_dict.get("dimensions")
        number_cells = cube_as_dict.get("number_cells")
        number_filled_cells = cube_as_dict.get("number_filled_cells")

        return cls(name=name, type=type_, id=id, dimensions=dimensions, number_cells=number_cells, number_filled_cells=number_filled_cells)

    def set_dimensions(cls, dims: list):

        cls.dimensions = dims

    def set_database(cls, database: Database):

        cls.database = database

    def set_number_of_rules(cls, number_of_rules: int):

        cls.number_of_rules = number_of_rules