from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DatabaseService import DatabaseService
from JedoxPy.Services.CubeService import CubeService
from JedoxPy.Services.ElementService import ElementService

from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Dimension import Dimension
from JedoxPy.Exceptions.Exceptions import *
from JedoxPy.Objects.Enums import TypeElement, SplashingTypes, DimensionType, DimensionProperty

class DimensionService():

    def __init__(self, connection: ConnectionService):
        self.connection = connection

    def _exists(self, database: Database, dimension: Dimension) -> bool:

        conn = self.connection
        db_service = DatabaseService(conn)

        if dimension.name in db_service.get_dimension_names_id(database=database).keys():
            return True

        return False

    def get(self, database: Database, dimension_name: str) -> Dimension:
        """ Gets a dimension

        :param database: instance of JedoxPy.Database
        :param dimension: string
        :return: object Dimension
        """

        try:

            element_service = ElementService(self.connection)

            service_method = "/dimension/info"
            payload = dict()
            payload["database"] = database.id
            payload["name_dimension"] = dimension_name

            # get virtual dimensions by default
            payload["show_virtual"] = 1

            result = self.connection.request(service_method=service_method, payload=payload, header=True)

            if result is None:
                return

            dimension = Dimension.from_dict(result)
            dimension.set_database(database=database)

            # get attribute dimension (only for normal dimensions)
            if dimension.type == DimensionType.NORMAL:
                attribute_dimension = f"#_{dimension_name}_"
                attribute_dimension_obj = self.get(database=database, dimension_name=attribute_dimension)

                #get attributes
                attributes = element_service.get_elements_by_name(dimension=attribute_dimension_obj)
                dimension.set_attributes( list( attributes.keys() ) )

            return dimension

        except JedoxPyNotFoundException as e:
            error_msg = f"Dimension {dimension_name} not found in database {database.name}"
            raise JedoxPyNotFoundException(error_code=e.error_code, custom_message=error_msg)

    def get_virtual_attributes(self, dimension: Dimension) -> list:
        """ Gets the virtual attributes of a dimension

        :param dimension: instance of JedoxPy.Dimension
        :return: list
        """

        from JedoxPy.Services.CellService import CellService

        cube_service = CubeService(connection=self.connection)
        cell_service = CellService(connection=self.connection)

        # get virtual dimensions using a get data export (cube #_<dim>_METAATRIBUTES
        meta_attr_cube_name = f"#_{dimension.name}_METAATTRIBUTES"
        meta_attr_cube = cube_service.get(database=dimension.database, cube_name=meta_attr_cube_name)

        conditions = [{"==": "1"}]
        virtual_attr_export = cell_service.get_data_export(cube=meta_attr_cube, area=["Virtual", "*", "*"], ignore_empty=True,condition=conditions)

        out_virtual = []
        for virtual_attr in virtual_attr_export:
            out_virtual.append(virtual_attr[1])

        return out_virtual

    def create(self, database: Database, dimension: str) -> Dimension:
        """ Create a dimension

        :param database: instance of JedoxPy.Database
        :param dimension: string
        :return: instance of JedoxPy.Dimension
        """

        try:
            conn = self.connection

            payload = dict()
            payload["database"] = database.id
            payload["new_name"] = dimension
            conn.request(service_method="/dimension/create", payload=payload, header=False)

            return self.get(database=database, dimension_name=dimension)

        except JedoxPyAlreadyExistsException:
            raise

    def rename(self, dimension: Dimension, new_name: str) -> Dimension:
        """ Rename a dimension

        :param dimension: instance of JedoxPy.Dimension
        :return: nothing
        """

        conn = self.connection
        db = dimension.database

        renamed_dim = Dimension(name=new_name)

        if self._exists(database=db, dimension=renamed_dim):
            raise JedoxPyObjectExistsException("Dimension", renamed_dim)

        else:
            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id
            payload["new_name"] = new_name
            conn.request("/dimension/rename", payload=payload, header=False)

            # query the renamed dimension
            return self.get(database=dimension.database, dimension_name=new_name)

    def delete(self, dimension: Dimension, drop_cubes: bool = False):
        """ Delete a dimension

        :param dimension: instance of JedoxPy.Dimension
        :param drop_cubes: bool
        :return: instance of JedoxPy.Dimension
        """

        try:
            cube_service = CubeService(connection=self.connection)

            payload=dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id

            cubes_where_used = self.get_cubes_using_dimension(dimension=dimension)

            if drop_cubes and len(cubes_where_used)>0:
                # delete all the cubes using the dimension
                print(f"dim is used in {len(cubes_where_used)} dimensions, dropping")
                for cube_where_used in cubes_where_used:
                    print(cube_where_used)
                    cube = cube_service.get(database=dimension.database, cube_name=cube_where_used)

                    cube_service.delete(cube=cube)

            # if not drop_cubes and len(cubes_where_used)>0:
            #     raise JedoxPyException(message=f"Dimension {dimension.name} is used in the cubes {",".join(cubes_where_used)}, delete the cubes first or use drop_cubes set to True")

            req = self.connection.request(service_method="/dimension/destroy", payload=payload, header=True)

            return req

        except JedoxPyDimensionErrorException as e:
            raise

    def get_cubes_using_dimension(self,
                                  dimension: Dimension,
                                  show_normal: bool=True,
                                  show_system: bool=False,
                                  show_attribute: bool=False,
                                  show_info: bool=False,
                                  show_gputype: bool=False):

        """ Get cubes using a dimension

        :param dimension: instance of JedoxPy.Dimension
        :param show_normal: bool
        :param show_system: bool
        :param show_attribute: bool
        :param show_system: bool
        :param show_info: bool
        :param show_gputype: bool
        :return: list
        """

        payload = dict()
        payload["database"] = dimension.database.id
        payload["dimension"] = dimension.id
        payload["show_normal"] = int(show_normal)
        payload["show_system"] = int(show_system)
        payload["show_attribute"] = int(show_attribute)
        payload["show_info"] = int(show_info)
        payload["show_gputype"] = int(show_gputype)

        cubes_req = self.connection.request(service_method="/dimension/cubes", payload=payload, header=True)

        cubes = []
        # must check if return is a dict or a list. monumental error, should return always a list, even if len(return)=1
        if isinstance(cubes_req, dict):
            cubes.append(cubes_req.get("name_cube"))
        else:
            for cube in cubes_req:
                cubes.append(cube.get("name_cube"))

        return cubes

    def create_attribute(self,
                         dimension: Dimension,
                         attribute_name: str,
                         attribute_type: TypeElement = TypeElement.STRING,
                         virtual: bool=False,
                         ignore_type_change: bool=True):

        """ Create attribute

        :param dimension: instance of JedoxPy.Dimension
        :param attribute_name: str
        :param attribute_type: instance of TypeELement
        :param virtual: bool
        :param ignore_type_change: bool
        :return: list
        """


        if virtual and attribute_type == TypeElement.NUMERIC:
            raise JedoxPyException("Virtual dimension cannot be created : virtual dimensions are only built from "
                                   "string attribute elements")

        element_service = ElementService(self.connection)

        database = dimension.database

        attribute_dimension_name = f"#_{dimension.name}_"

        # no need to create the attribute dimension, since it is created automatically
        attribute_dimension = self.get(database=database, dimension_name=attribute_dimension_name)

        # create attribute name
        element_service.create_or_update(database=database,
                                         dimension=attribute_dimension,
                                         name=attribute_name,
                                         type=attribute_type,
                                         ignore_type_change=ignore_type_change)

        if virtual:
            self.activate_virtual(dimension=dimension, attribute_name=attribute_name)

    # TO DO : refactor, attribute_name as Attribute Object
    def activate_virtual(self, dimension: Dimension, attribute_name: str ):

        payload = dict()
        payload["database"] = dimension.database.id
        payload["dimension"] = dimension.id
        payload["name_attribute"] = attribute_name
        payload["activate"] = "1"

        self.connection.request(service_method="/dimension/activate_virtual", payload=payload, header=False)

    def set_dimension_property(self, dimension: Dimension, property: DimensionProperty, value: str):
        """ Set dimension property

        :param property: instance of JedoxPy.Dimension
        :param property: instance of DimensionProperty
        :param value: string
        :return: bool
        """

        from JedoxPy.Services.CellService import CellService

        cube_service = CubeService(connection=self.connection)
        cell_service = CellService(connection=self.connection)
        dim_prop_cube = cube_service.get(database=dimension.database, cube_name="#_#_DIMENSION_")

        target_coords = [property.value, dimension.name]

        return cell_service.set_cell_data(cube=dim_prop_cube, coordinates=target_coords, value=value)