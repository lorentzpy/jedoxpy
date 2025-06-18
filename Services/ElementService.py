from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.SubsetService import SubsetService
from JedoxPy.Services.CubeService import CubeService
#from JedoxPy.Services.SubcubeService import SubcubeService


from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Dimension import Dimension
from JedoxPy.Objects.Element import Element
from JedoxPy.Objects.Subset import Subset, HierarchyFilter, SortingFilter
from JedoxPy.Objects.Enums import TypeElement, HierarchyFilterTypes, SortingCriteria, DimensionLoadModes

from JedoxPy.Exceptions.Exceptions import JedoxPyNotFoundException, JedoxPyAlreadyExistsException, JedoxPyException

import string
import random

import pandas as pd

OMIT_HEADER = 0x01
OMIT_ROWS = 0x02
OMIT_COLUMNS = 0x04
OMIT_AREA = 0x08
RETURN_SUBSET_NAMES = 0x10
COMPRESS_RESULT = 0x0200
RETURN_ONLY_AXES_SIZES = 0x0400
SEND_PARENT_PATHS = 0x80


class ElementService:

    def __init__(self, connection: ConnectionService):

        self._connection = connection

    def get_by_name(self, dimension: Dimension, element: str):
        service_method = "/element/info"
        payload = dict()
        payload["database"] = dimension.database.id
        payload["dimension"] = dimension.id
        payload["name_element"] = element

        try:
            result = self._connection.request(service_method=service_method, payload=payload, header=True)

            element_obj = Element.from_dict(result)

            element_obj.set_database(database=dimension.database)

            return element_obj

        except JedoxPyNotFoundException as e:
            error_msg = f"Element {element} not found in dimension {dimension.name}"
            raise JedoxPyNotFoundException(error_code=e.error_code, custom_message=error_msg)

    def get_by_id(self, dimension: Dimension, element: int):

        try:
            service_method = "/element/info"
            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id
            payload["element"] = element

            result = self._connection.request(service_method=service_method, payload=payload, header=True)

            element_obj = Element.from_dict(result)

            element_obj.set_database(database=dimension.database)

            return element_obj

        except JedoxPyNotFoundException as e:
            error_msg = f"Element with id {element} not found in dimension {dimension.name}"
            raise JedoxPyNotFoundException(error_code=e.error_code, custom_message=error_msg)

    # still needed ?
    def exists(self, dimension: Dimension, element: str):

        elements = self.get_by_name(dimension=dimension, element=element)

        if element in elements:
            return True

        return False

    def get_base_elements(self, dimension: Dimension, element: str) -> dict:

        try:
            subset_service = SubsetService(connection=self._connection)

            # create subset
            subset = Subset(connection=self._connection, dimension=dimension)

            # create hierarchy filter (direction below, only bases)
            hierarchy_filter = HierarchyFilter(element=element, direction="below", filter_type=HierarchyFilterTypes.BASE)

            subset.add_filter(hierarchy_filter)

            # execute subset
            children = subset_service.execute_subset(subset)

            return children

        except JedoxPyException:
            raise

    def get_elements_info(self, dimension: Dimension) -> list:

        try:
            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id

            result = self._connection.request(service_method="/dimension/elements", payload=payload, header=True)

            # TO DO : refactor output of the rest api, it should always return a list!!!
            if isinstance(result, dict):
                result = [result]

            return result

        except JedoxPyNotFoundException:
            raise

    def get_elements_by_id(self, dimension: Dimension) -> dict:
        """

        :param dimension: the dimension object
        :return: a dict with ids as keys, and names as values
        """

        try:
            result = self.get_elements_info(dimension=dimension)

            dim_as_dict = dict()
            for item in result:
                dim_as_dict[int(item["element"])] = item["name_element"]

            return dim_as_dict

        except JedoxPyException:
            raise

    def get_elements_by_name(self, dimension: Dimension) -> dict:
        """

        :param database: the database object
        :param dimension: the dimension object
        :return: a dict with names as keys, and ids as values
        """

        try:
            result = self.get_elements_info(dimension=dimension)

            dim_as_dict = dict()
            for item in result:
                dim_as_dict[item["name_element"]] = item["element"]

            return dim_as_dict

        except JedoxPyException:
            raise

    def rename(self, dimension: Dimension, element_to_rename: Element, new_name: str) -> Element:

        try:
            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id
            payload["element"] = element_to_rename.id
            payload["new_name"] = new_name

            self._connection.request(service_method="/element/rename", payload=payload, header=False)

            updated_object = self.get_by_name(dimension=dimension, element=new_name)

            return updated_object

        except JedoxPyAlreadyExistsException:
            raise

    def delete(self, dimension: Dimension, name: str):

        try:
            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id
            payload["name_element"] = name

            res = self._connection.request(service_method="/element/destroy", payload=payload, header=False)

        except JedoxPyException:
            raise

    def get_elements_dataframe(self, dimension: Dimension, element: str, show_weights: bool=False, show_types: bool=False, attributes: list | bool=None, languages: bool=False) -> 'pd.DataFrame':

        from JedoxPy.Services.CellService import CellService

        subset_service = SubsetService(connection=self._connection)
        cube_service = CubeService(connection=self._connection)
        cell_service = CellService(connection=self._connection)

        subset = Subset(connection=self._connection, dimension=dimension)
        hierarchyFilter = HierarchyFilter(element=element, direction="below")

        sorting = SortingFilter(sorting_criterium=SortingCriteria.SORT_ON_CONSO)
        subset.add_filter(sorting)
        subset.add_filter(hierarchyFilter)

        elts = subset_service.execute_subset(subset=subset)

        if attributes is True:
            # query all the attributes for the dimension
            attributes = dimension.attributes

        # attributes is a fixed list
        if isinstance(attributes, list):
            cube_name = f"#_{dimension.name}"
            attribute_dimension = f"{cube_name}_"
            attribute_cube = cube_service.get(database=dimension.database, cube_name=cube_name)

            language = "*" if languages else "~"
            area_attributes = [attributes, "*", language]

            # query attributes data, with rules and conso (attributes (numerical or strings) can be on top level)
            df_attributes = cell_service.get_data_as_dataframe(cube=attribute_cube, area=area_attributes, use_rules=True, base_only=False)

            pivot_columns = [attribute_dimension, "#_LANGUAGE"]

            df_attributes = df_attributes.pivot_table(
                index=dimension.name,
                columns=pivot_columns,
                values="Value",
                aggfunc="first"
            )

            # rename if several languages
            if languages:
                df_attributes.columns = [f"{attr} ({lang})" for attr, lang in df_attributes.columns]
            else:
                df_attributes.columns = [f"{attr[0]}" for attr in df_attributes.columns]

            df_attributes.reset_index(inplace=True)

        df_data = list()
        for dimension_element_id, dimension_element_properties in elts.items():

            name = dimension_element_properties.get("name_element")
            type = TypeElement(int(dimension_element_properties.get("type"))).name[0]

            out_item = list()
            # add element as a child without a parent if no parent
            if dimension_element_properties.get("parents") == "":

                out_item = ["",name]
                if show_types:
                    out_item.append(type)

                if show_weights:
                    out_item.append(1)

                df_data.append(tuple(out_item))

            # append children and their parents
            if dimension_element_properties.get("children") is not None:
                children = dimension_element_properties.get("children")
                weights = dimension_element_properties.get("weights")
                # split children as list
                children_list = children.split(",")
                weights_list = weights.split(",")

                out_item = list()
                for child_index, child in enumerate(children_list):

                    out_item = [name,elts.get(str(child)).get("name_element")]
                    if show_types:
                        type = TypeElement(int(elts.get(str(child)).get("type"))).name[0]
                        out_item.append(type)

                    if show_weights:
                        weight = weights_list[child_index]
                        out_item.append(float(weight))

                    df_data.append(tuple(out_item))

        columns = ["parent", "child"]
        if show_types:
            columns.append("node_type")

        if show_weights:
            columns.append("weight")

        df_pc = pd.DataFrame(data=df_data, columns=columns)

        #merge df and df_attributes
        if attributes is not None:
            df = pd.merge(left=df_pc, right=df_attributes, left_on="child", right_on=dimension.name).drop(columns=[dimension.name])
        else:
            df = df_pc

        # remove the empty values
        df.fillna(value="", inplace=True)
        return df

    def create_or_update(self,
                         database: Database,
                         dimension: Dimension,
                         name: str,
                         type: TypeElement,
                         children: list=None,
                         weights: list = None,
                         ignore_type_change=True):

        payload = dict()
        payload["database"] = database.id
        payload["dimension"] = dimension.id
        payload["name_element"] = name
        payload["type"] = type.value

        if not ignore_type_change:
            # check if element already exists
            if self.exists(dimension=dimension, element=name):
                element_obj = self.get_by_name(dimension=dimension, element=name)
                element_type = element_obj.type
                if element_type != type:
                    raise JedoxPyException(f"Element {name} already exist as type {element_type}")

        if type == TypeElement.CONSOLIDATED:
            payload["name_children"] = ",".join(children)

            if weights is not None:
                if len(weights) != len(children):
                    raise JedoxPyException(f"Weights list must be same length as children list")

                payload["weights"] = ",".join(map(str, weights))

        # use of /element/update, if the element exists it won't do anything (behaviour of Integrator)
        # if the element does not exist, it will be created
        res = self._connection.request(service_method="/element/replace", payload=payload, header=False)

    def create_base_element(self, dimension: Dimension, element_name: str, element_type: TypeElement=TypeElement.NUMERIC):

        try:
            conn = self._connection

            service_method = "/element/create"

            payload = dict()
            payload["database"] = dimension.database.id
            payload["dimension"] = dimension.id
            payload["new_name"] = element_name
            payload["type"] = TypeElement.NUMERIC.value

            conn.request(service_method=service_method, payload=payload, header=False)

        except JedoxPyException as e:
            error_msg = f"Element {element_name} already exists in dimension {dimension.name}"
            raise JedoxPyException(error_code=e.error_code, error_msg=error_msg)

    # def write_elements_dataframe(self, dimension: Dimension, df: 'pd.DataFrame', parent_column: str= "parent", child_column: str= "child", element_load_mode: DimensionLoadModes=DimensionLoadModes.ADD ):
    # data : list of tuples with parent, child
    def write_elements(self, dimension: Dimension, pc_data: list, element_load_mode: DimensionLoadModes=DimensionLoadModes.ADD ):

        #from JedoxPy.Services.DimensionService import DimensionService

        # parent, child as a structure
        # get all elements
        all_elements = list(dict.fromkeys([item for t in pc_data for item in t]))

        # get the whole dimension
        current_dimension = list(self.get_elements_by_name(dimension=dimension).keys())

        name_elements = ",".join(all_elements)
        type_elements = ",".join(["1"] * len(all_elements))

        payload = dict()
        payload["database"] = dimension.database.id
        payload["dimension"] = dimension.id

        if element_load_mode == DimensionLoadModes.DELETE:
            payload_delete = payload

            # get unique elements (parents & children)
            elements_delete = list(set(all_elements))

            if len(elements_delete) > 0:
                payload["name_elements"] = ",".join(elements_delete)

                # launch destroy call
                self._connection.request(service_method="/element/destroy_bulk", payload=payload, header=False)

        if element_load_mode == DimensionLoadModes.UPDATE:
            pass

        payload["name_elements"] = name_elements
        payload["types"] = type_elements

        # load elements
        req = self._connection.request(service_method="/element/create_bulk",payload=payload, header=False)

