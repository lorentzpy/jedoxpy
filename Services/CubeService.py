from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DatabaseService import DatabaseService
from JedoxPy.Services.RulesService import RulesService
from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Cube import Cube
from JedoxPy.Exceptions.Exceptions import JedoxPyRequestException, JedoxPyNotFoundException, JedoxPyAlreadyExistsException
from JedoxPy.Objects.Enums import TypeObject

class CubeService:


    def __init__(self, connection: ConnectionService):
        self._connection = connection

    def get(self, database: Database, cube_name: str) -> 'Cube':
        """ Get a cube

        :param database: instance of JedoxPy.Database
        :param cube_name: str
        :return: instance of JedoxPy.Cube
        """

        try:

            payload = dict()
            payload["database"] = database.id
            payload["name_cube"] = cube_name

            # always get virtual dims to ease the handling of virtual coordinates
            payload["show_virtual"] = 1

            connection = self._connection
            result = connection.request(service_method="/cube/info", payload=payload, header=True)

            cube = Cube.from_dict(cube_as_dict=result)

            # set the database property
            cube.set_database(database=database)

            # set the dimensions property with the dimension names
            dimensions = self.get_cube_dimensions(cube=cube)
            cube.set_dimensions(dims=dimensions)

            number_of_rules = RulesService(connection=self._connection).get_number_of_rules(cube=cube)
            cube.set_number_of_rules(number_of_rules=number_of_rules)

            return cube

        except JedoxPyNotFoundException as e:
            error_msg = f"Cube {cube_name} not found in database {database.name}"
            raise JedoxPyNotFoundException(error_code=e.error_code, custom_message=error_msg)

    def get_cube_dimensions(self, cube: Cube) -> list:
        """ Get the dimensions of a cube as a list of strings or tuples if virtual

        :param cube: instance of JedoxPy.Cube
        :return: list
        """

        try:

            database_service = DatabaseService(self._connection)

            database = cube.database

            show_system = False
            show_attribute = False
            show_info = False

            if cube._type == TypeObject.SYSTEM:
                show_system = True
            elif cube._type == TypeObject.ATTRIBUTE:
                show_attribute = True
                show_system = True # #_LANGUAGE is a system dim

            server_dimensions = database_service.get_dimension_id_names(database=database,
                                                                        show_virtual_attribute=True,
                                                                        show_system=show_system,
                                                                        show_attribute=show_attribute,
                                                                        show_info=show_info)

            dim_ids = cube.dimensions

            dim_names = list()
            for dim_id in dim_ids:
                dim_name = server_dimensions.get(dim_id, "dim not foundb")
                if dim_name.startswith("#_VIRTUAL_"):
                    # build tuple with dimname, attributename
                    split_dim_name = dim_name.split(sep="_")
                    dim_names.append((split_dim_name[2], split_dim_name[4]))
                else:
                    dim_names.append(dim_name)

            return dim_names

        except JedoxPyRequestException as e:
            raise

    def create(self, database: Database, name: str, dimensions: list) -> Cube:
        """ Create a cube

        :param database: instance of JedoxPy.Database
        :param name: str
        :param dimensions: list
        :return: instance of JedoxPy.Cube
        """

        try:
            service_method = "/cube/create"

            payload = dict()
            payload["database"] = database.id
            payload["new_name"] = name
            payload["name_dimensions"] = ",".join(dimensions)

            self._connection.request(service_method=service_method, payload=payload, header=True)

            return self.get(database=database, cube_name=name)

        except JedoxPyNotFoundException as e:
            error_msg = f"{e.jedox_object_type} {e.jedox_object} not found in database {database.name}"
            raise JedoxPyNotFoundException(error_code=e.error_code, custom_message=error_msg)

    def rename(self, cube: Cube, new_name: str) -> Cube:
        """ Renames a cube

        :param cube: instance of JedoxPy.Cube
        :param new_name: str
        :return: updated instance of JedoxPy.Cube
        """

        try:
            service_method = "/cube/rename"

            payload = dict()
            payload["database"] = cube.database.id
            payload["cube"] = cube.id
            payload["new_name"] = new_name

            self._connection.request(service_method=service_method, payload=payload, header=False)

            # get the updated cube
            updated_cube = self.get(database=cube.database, cube_name=new_name)

            return updated_cube

        except JedoxPyAlreadyExistsException as e:
            error_msg = f"{e.jedox_object_type} {e.jedox_object} already exists in database {cube.database.name}"
            raise JedoxPyAlreadyExistsException(error_code=e.error_code, custom_message=error_msg)


    def delete(self, cube: Cube):
        """ Deletes a cube

        :param cube: instance of JedoxPy.Cube
        :return: bool
        """

        try:
            service_method = "/cube/destroy"

            payload = dict()
            payload["database"] = cube.database.id
            payload["cube"] = cube.id

            result = self._connection.request(service_method=service_method, payload=payload, header=False)

            return result["OK"]

        except JedoxPyRequestException:
            raise

    def clear(self, cube: Cube, subcube: list = None, complete: bool = False) -> Cube:
        """ Clears a cube

        :param cube: instance of JedoxPy.Cube
        :param subcube: list
        :param complete: bool
        :return: bool
        """

        try:
            service_method = "/cube/clear"

            payload = dict()
            payload["database"] = cube.database.id
            payload["cube"] = cube.id
            payload["name_area"] = ",".join(subcube)
            payload["complete"] = +complete

            self._connection.request(service_method=service_method, payload=payload)

            # return updated cube object
            return self.get(database=cube.database, cube_name=cube.name)

        except JedoxPyRequestException:
            raise


    def get_locks(self, cube: Cube, area: list = None, user: str=None) -> list:
        """ Clears a cube

        :param cube: instance of JedoxPy.Cube
        :param area: list
        :param user: str
        :return: list
        """
        try:
            service_method = "/cube/locks"
            payload = dict()
            payload["database"] = cube.database.id
            payload["cube"] = cube.id

            if area is not None:
                payload["name_area"] = area

            if user is not None:
                payload["user"] = user

            res = self._connection.request(service_method=service_method, payload=payload)

            return res

        except JedoxPyRequestException as e:
            raise

    def update_rule_templates(self, cube: Cube) -> bool:
        """ Update the rule templates for a cube

        :param cube: instance of JedoxPy.Cube
        :return: bool
        """
        try:

            rule_service = RulesService(self._connection)

            # get list or rule templates
            rule_templates = rule_service.get_list(cube=cube, rule_templates=True, generated=False, regular=False)

            for rule_template in rule_templates:

                # create a rule object for each
                rule_obj = rule_service.get_rule_by_id(cube=cube, rule_id=rule_template.get("rule"))

                # trigger activation only for active rule templates
                if rule_obj.rule_active:
                    rule_service.activate(rule_obj)

            return True

        except JedoxPyRequestException:
            raise
