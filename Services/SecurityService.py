from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DatabaseService import DatabaseService
from JedoxPy.Services.CubeService import CubeService
from JedoxPy.Services.DimensionService import DimensionService
from JedoxPy.Services.CellService import CellService
from JedoxPy.Services.ElementService import ElementService

from JedoxPy.Objects.Enums import TypeElement
from JedoxPy.Objects.Security import User, Group, Role

from JedoxPy.Exceptions.Exceptions import JedoxPyException, JedoxPyNotDeletableException

from enum import Enum

class SecurityObjectType(Enum):

    USER = "#_USER_"
    GROUP = "#_GROUP_"
    ROLE = "#_ROLE_"

class SecurityService:

    def __init__(self, connection: ConnectionService):

        self._connection = connection
        # System db has always the id 0
        self._database = DatabaseService(connection=connection).get(name="System")

    def get_security_elements(self, security_object_type: SecurityObjectType) -> dict:

        dimension_service = DimensionService(self._connection)
        element_service = ElementService(self._connection)

        sec_dim = dimension_service.get(self._database, dimension_name=security_object_type.value)

        return element_service.get_elements_by_id(dimension=sec_dim)

    def get_security_elements_by_name(self, security_object_type: SecurityObjectType) -> dict:

        security_elements = self.get_security_elements(security_object_type)

        return {v: k for k, v in security_elements.items()}

    def delete_security_element(self, security_object_type: SecurityObjectType, security_object: User|Group|Role):

        dimension_service = DimensionService(self._connection)
        element_service = ElementService(self._connection)

        security_dimension = dimension_service.get(self._database, security_object_type.value)

        element_service.delete(dimension=security_dimension, name=security_object.name)

    def get_user(self, name: str) -> User:

        user_props_cube = CubeService(self._connection).get(self._database, "#_USER_USER_PROPERTIES")

        cells = CellService(self._connection).get_data_export(cube=user_props_cube, area=[name, "*"], base_only=True)

        result = {item[1]: item[2] for item in cells}

        result["id"] = self.get_security_elements_by_name(SecurityObjectType.USER).get(name)
        result["name"] = name

        # rename LastLoginTime to last_login
        result["last_login"] = result.pop("LastLoginTime", 0)

        user = User.fromdict(user_as_dict=result)

        user.set_groups(self.get_user_groups(user=user))

        return user

    def delete_user(self, user: User):

        try:
            self.delete_security_element(security_object_type=SecurityObjectType.USER, security_object=user)

        except JedoxPyNotDeletableException as e:
            raise

    def create_user(self, user: User):

        try:
            # create user element
            dim_service = DimensionService(connection=self._connection)
            user_dim = dim_service.get(database=self._database, dimension_name="#_USER_")

            element_service = ElementService(connection=self._connection)

            element_service.create_base_element(dimension=user_dim, element_name=user.name, element_type=TypeElement.STRING)

            # set full_name
            cell_service = CellService(connection=self._connection)
            cube_service = CubeService(connection=self._connection)

            user_props_cube = cube_service.get(database=self._database, cube_name="#_USER_USER_PROPERTIES")

            cell_service.set_cell_data(value=user.full_name, cube=user_props_cube, coordinates=[user.name, "fullName"])
            cell_service.set_cell_data(value=user.description, cube=user_props_cube, coordinates=[user.name, "description"])

            return self.get_user(name=user.name)

        except JedoxPyException as e:
            raise

    def set_password(self, user: User, password: str):

        conn = self._connection

        method = "/server/change_password"

        payload = dict()
        payload["user"] = user.name
        payload["password"] = password

        conn.request(service_method=method, payload=payload, header=False)

    def get_group(self, name: str) -> Group:

        group_props_cubes = CubeService(self._connection).get(self._database, cube_name="#_GROUP_GROUP_PROPERTIES")

        cells = CellService(self._connection).get_data_export(cube=group_props_cubes, area=[name, "*"], base_only=True)

        result = {item[1]: item[2] for item in cells}

        result["id"] = self.get_security_elements_by_name(SecurityObjectType.GROUP).get(name)
        result["name"] = name

        group = Group.fromdict(group_as_dict=result)

        group.set_roles(self.get_group_roles(group=group))

        return group

    def delete_group(self, group: Group):

        try:
            self.delete_security_element(security_object_type=SecurityObjectType.GROUP, security_object=group)

        except JedoxPyNotDeletableException as e:
            raise


    def get_role(self, name: str) -> Role:

        try:
            role_props_cube = CubeService(self._connection).get(self._database, cube_name="#_ROLE_ROLE_PROPERTIES")

            cells = CellService(self._connection).get_data_export(cube=role_props_cube, area=[name, "*"], base_only=True)

            result = {item[1]: item[2] for item in cells}

            result["id"] = self.get_security_elements_by_name(SecurityObjectType.ROLE).get(name)
            result["name"] = name

            role = Role.fromdict(role_as_dict=result)

            role.set_groups(self.get_role_groups(role))

            return role

        except JedoxPyException as e:
            raise

    def delete_role(self, role: Role):
        try:
            self.delete_security_element(security_object_type=SecurityObjectType.ROLE, security_object=role)

        except JedoxPyNotDeletableException as e:
            raise

    def get_user_groups(self, user: User):

        user_group_cube = CubeService(self._connection).get(database=self._database, cube_name="#_USER_GROUP")

        user_group_allocations = CellService(self._connection).get_data_export(cube=user_group_cube,
                                                                               area=[user.name, "*"],
                                                                               ignore_empty=True)

        user_groups = []
        for user_group_allocation in user_group_allocations:
            user_groups.append(user_group_allocation[1])

        return user_groups

    # set user to group (or group to user)
    def set_user_group(self, user: User, group: Group):

        user_group_cube = CubeService(self._connection).get(self._database, cube="#_USER_GROUP")

        #CellService(self._connection).set_cell_data(value="1", cube=user_group_cube,coordinates=[user.name, group.name] )

        user.set_groups(groups=self.get_user_groups(user=user))

    def get_group_roles(self, group: Group):

        group_role_cube = CubeService(self._connection).get(self._database, cube_name="#_GROUP_ROLE")

        group_role_allocations = CellService(self._connection).get_data_export(cube=group_role_cube,
                                                                               area=[group.name, "*"],
                                                                               ignore_empty=True)

        group_roles = []

        for group_role_allocation in group_role_allocations:
            group_roles.append(group_role_allocation[1])

        return group_roles

    def get_role_groups(self, role: Role):

        role_group_cube = CubeService(self._connection).get(self._database, cube_name="#_GROUP_ROLE")

        role_group_allocations = CellService(self._connection).get_data_export(cube=role_group_cube,
                                                                               area=["*", role.name],
                                                                               ignore_empty=True)

        role_groups = []
        for role_group_allocation in role_group_allocations:
            role_groups.append(role_group_allocation[0])

        return role_groups