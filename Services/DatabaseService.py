from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Cube import Cube
from JedoxPy.Exceptions.Exceptions import *


class DatabaseService:

    def __init__(self, connection: ConnectionService):
        self.connection = connection

    def get(self, name) -> Database:
        """ Get a cube

        :param database: instance of JedoxPy.Database
        :param cube_name: str
        :return: instance of JedoxPy.Cube
        """
        try:

            service_method = "/database/info"

            payload = dict()
            payload["name_database"] = name

            result = self.connection.request(service_method=service_method, payload=payload, header=True)

            return Database.from_dict(result)

        except JedoxPyDatabaseErrorException as e:
            raise

    def create(self, name: str) -> Database:
        """ Create a database

        :param name: str
        :return: instance of JedoxPy.Database
        """
        try:
            service_method = "/database/create"
            payload = dict()
            payload["new_name"] = name

            result = self.connection.request(service_method=service_method, payload=payload, header=True)

            return Database.from_dict(result)

        except JedoxPyAlreadyExistsException:
            raise

    def rename(self, database: Database, new_name) -> Database:
        """ Renames a database

        :param database: instance of JedoxPy.Database
        :param new_name: str
        :return: updated instance of JedoxPy.Database
        """
        try:
            # rename database
            service_method = "/database/rename"
            payload = dict()
            payload["database"] = database.id
            payload["new_name"] = new_name

            result = self.connection.request(service_method=service_method, payload=payload, header=True)

            renamed_database = self.get(name=new_name)

            return renamed_database

        except JedoxPyNotChangableException:
            raise

    def delete(self, database: Database) -> bool:
        """ Deletes a database

        :param database: instance of JedoxPy.Database
        :return: bool
        """
        try:
            # delete database
            service_method = "/database/destroy"
            payload = dict()
            payload["database"] = database.id

            result = self.connection.request(service_method=service_method, payload=payload, header=True)

            return result["OK"]

        except JedoxPyNotDeletableException:
            raise

    def get_cubes(self, database: Database, show_system: bool = False) -> list[Cube]:
        """ Get the cubes of a database

        :param database: instance of JedoxPy.Database
        :param show_system: bool
        :return: list[Cube]
        """
        try:

            from JedoxPy.Services.CubeService import CubeService

            db_id = database.id

            service_method = "/database/cubes"

            payload = dict()
            payload["database"] = db_id
            payload["show_system"] = +(show_system)

            cubes = self.connection.request(service_method=service_method, payload=payload, header=True)

            cube_service = CubeService(self.connection)

            cube_objects = []
            for cube in cubes:
                cube_objects.append(cube_service.get(database=database, cube_name=cube.get("name_cube")))

            return cube_objects

        except JedoxPyException:
            raise

    def get_cube_names(self, database: Database, show_system: bool = False) -> list:
        """ Get the cube names of a database

        :param database: instance of JedoxPy.Database
        :param show_system: bool
        :return: list
        """

        cubes = self.get_cubes(database=database, show_system=show_system)

        return [cube.name for cube in cubes]

    def get_dimension_id_names(self,
                               database: Database,
                               show_normal: bool = True,
                               show_system: bool = False,
                               show_info: bool = False,
                               show_attribute: bool = False,
                               show_virtual_attribute: bool = False) -> dict:
        """ Get the dimensions of a database as a dict, keys are the dimension ids

        :param database: instance of JedoxPy.Database
        :param show_normal: bool
        :param show_system: bool
        :param show_info: bool
        :param show_attribute: bool
        :param show_virtual_attribute: bool
        :return: dict
        """

        try:

            db_id = database.id
            payload = dict()
            payload["database"] = db_id
            payload["show_normal"] = +show_normal
            payload["show_system"] = +show_system
            payload["show_info"] = +show_info
            payload["show_attribute"] = +show_attribute
            payload["show_virtual_attribute"] = +show_virtual_attribute

            result = self.connection.request(service_method="/database/dimensions", payload=payload, header=True)

            dim_dict = dict()
            for dim in result:
                dim_dict[int(dim["dimension"])] = dim["name_dimension"]

            return dim_dict

        except JedoxPyException:
            raise

    def get_dimension_names_id(self,
                               database: Database,
                               show_normal: bool = True,
                               show_system: bool = False,
                               show_info: bool = False,
                               show_attribute: bool = False,
                               show_virtual_attribute: bool = False) -> dict:

        """ Get the dimensions of a database as a dict, keys are the dimension ids

        :param database: instance of JedoxPy.Database
        :param show_normal: bool
        :param show_system: bool
        :param show_info: bool
        :param show_attribute: bool
        :param show_virtual_attribute: bool
        :return: dict
        """

        dimension_id_names = self.get_dimension_id_names(database=database,
                                                         show_normal=show_normal,
                                                         show_system=show_system,
                                                         show_info=show_info,
                                                         show_attribute=show_attribute,
                                                         show_virtual_attribute=show_virtual_attribute)

        return dict(zip(dimension_id_names.values(), dimension_id_names.keys()))
