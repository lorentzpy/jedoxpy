from JedoxPy.Objects.Enums import TypeObject,DatabaseStatus


class Database:

    def __init__(self, name: str, type_: int, id: int, status: int, number_cubes: int, number_dimensions: int):

        self.name = name
        self.type = TypeObject(type_)
        self.id = id
        self.status = DatabaseStatus(status)
        self.number_cubes = number_cubes
        self.number_dimensions = number_dimensions

    def __str__(self):
        return (f"Object {self.__class__.__name__} {self.name} (id {self.id}). "                
                f"Id: {self.id} ; "
                f"Type: {self.type.name} ; "
                f"Status: {self.status.name} ; "
                f"Number of cubes: {self.number_cubes} ; "
                f"Number of dimensions: {self.number_dimensions}"
                )

    def __repr__(self):
        return (f"Database(name={self.name},"
                f"Id={self.id},"
                f"Type={self.type.name})")


    @classmethod
    def from_dict(cls, database_as_dict) -> 'Database':
        name = database_as_dict.get("name_database")
        type_ = database_as_dict.get("type")
        id = database_as_dict.get("database")
        status = database_as_dict.get("status")
        number_cubes = database_as_dict.get("number_cubes")
        number_dimensions = database_as_dict.get("number_dimensions")


        return cls(name=name, type_=type_, id=id, status=status, number_cubes=number_cubes, number_dimensions=number_dimensions)