from JedoxPy.Objects.JedoxObject import JedoxObject
from JedoxPy.Objects.Enums import TypeElement
from JedoxPy.Objects.Database import Database


class Element:

    def __init__(self, name: str, type: int, id):
        self.name = name
        self.id = id if id is not None else None
        self.type = TypeElement(type)

    def __str__(self):
        return (f"Object {self.__class__.__name__} in database {self.database.name} (id {self.database.id}) "
                f"Name: {self.name} ; "
                f"Id: {self.id} ; "
                f"Type: {self.type.name}")

    def __repr__(self):
        return (f"Element(name={self.name},"
                f"Id={self.id},"
                f"Type={self.type.name})")

    @classmethod
    def from_dict(cls, element_as_dict) -> 'Element':
        name = element_as_dict.get("name_element")
        type_ = element_as_dict.get("type")
        id = element_as_dict.get("element")

        return cls(name=name, type=type_, id=id)

    def set_database(cls, database: Database):
        cls.database = database
