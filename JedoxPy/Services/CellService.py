import pandas as pd
from pandas import DataFrame

from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DatabaseService import DatabaseService
from JedoxPy.Services.CubeService import CubeService
from JedoxPy.Services.DimensionService import DimensionService
from JedoxPy.Services.ElementService import ElementService
from JedoxPy.Services.SubsetService import SubsetService

from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Cube import Cube

from typing import Optional, Iterable

from JedoxPy.Exceptions.Exceptions import JedoxPyException
from JedoxPy.Objects.Enums import SplashingTypes, Operator

import urllib.parse


class CellService:

    def __init__(self, connection: ConnectionService):

        self._connection = connection

    def get_cell_data(self, cube: Cube, coordinates: Iterable[str], virtual: dict = None):

        payload = dict()

        payload["database"] = cube.database.id
        payload["cube"] = cube.id

        cube_dims = cube.dimensions

        if virtual is None:
            cube_dims = [x for x in cube_dims if not isinstance(x, tuple)]

        # if coords is a dict, take the values, sorted
        if isinstance(coordinates, dict):
            coordinates = list({key: coordinates[key] for key in cube_dims}.values())

        # change the format of the virtual coordinates : {("dim_name","attribute"):"value"}
        virtual_coords = dict()
        if virtual is not None:
            for virtual_dim, virtual_attr_pairs in virtual.items():
                for virtual_attr, virtual_value in virtual_attr_pairs.items():
                    virtual_coords[(virtual_dim, virtual_attr)] = virtual_value

        out_coords_virt = []
        if virtual is not None:
            for cube_dim in cube_dims:
                virtual_dim = cube_dim[1]
                if isinstance(cube_dim, tuple):
                    if virtual_coords.get(cube_dim) is not None:
                        # append the virtual dim element
                        out_coords_virt.append(virtual_coords.get(cube_dim))
                    else:
                        # the virtual dim is not specified => take the default element (=> name of the dim)
                        out_coords_virt.append(virtual_dim)

        coordinates = coordinates + out_coords_virt

        payload["name_path"] = ",".join(coordinates)

        req = self._connection.request(service_method="/cell/value", payload=payload)

        if not req.get("exists"):
            return 0

        return req.get("value")

    # virtual: list of dicts, format:
    # {"<dim>":{"attribute1":"<attribute_value>", "attribute2":"<attribute value>"}}
    def get_filled_base_cell_count(self, database: Database, cube: Cube, area: list):

        cube_service = CubeService(self._connection)

        # get cube
        cube_obj = cube

        # get cube dimensions
        cube_dims = cube_service.get_cube_dimensions(cube=cube)

        # get data
        service_method = "/cell/area"
        payload = dict()
        payload["database"] = database.id
        payload["cube"] = cube_obj.id
        payload["function"] = 2

        coordinates = area
        coordinates_size = len(coordinates)
        expands = list()

        for area_id, area_ele in enumerate(area):
            if isinstance(area_ele, list):
                coordinates[area_id] = ':'.join(area_ele)

        expands = ['4'] * coordinates_size

        payload["expand"] = ",".join(expands)

        payload["name_area"] = ",".join(coordinates)

        result_data = self._connection.request(service_method=service_method, payload=payload, header=False)

        data = result_data
        if not any(isinstance(item, list) for item in data):  #len(data) == 1:
            data = [data]

        result_df = pd.DataFrame(data=data, columns=["type", "exists", "value", "path"])
        result_df["value"] = pd.to_numeric(result_df["value"])

        count = result_df["value"].sum()

        return count

    def get_drillthrough(self, cube: Cube, area: list, with_header: bool=False) -> list:

        service_method = "/cell/drillthrough"
        payload = dict()
        payload["database"] = cube.database.id
        payload["cube"] = cube.id
        payload["name_path"] = ",".join(area)
        payload["mode"] = 1

        result_data = self._connection.request(service_method=service_method, payload=payload, header=False)

        if not with_header:
            del(result_data[0])

        return result_data

    def get_drillthrough_dataframe(self, cube: Cube, area: list) -> pd.DataFrame:

        kwargs = locals()
        kwargs["with_header"] = True
        kwargs.pop("self")

        data = self.get_drillthrough(**kwargs)

        df_columns = data.pop(0)

        df = pd.DataFrame(data=data, columns=df_columns)

        return df

    # get dimensions with ids and names

    def get_data_export(self, cube: Cube, area: list, blocksize: int = 1000, base_only: bool = True,
                        ignore_empty: bool = False, use_rules: bool = False, condition: list[dict] = None,
                        condition_operator: Operator = Operator.AND, virtual: dict = None,
                        with_header: bool = False) -> list:

        """ Gets an export as a list
        :param cube: instance of JedoxPy.Cube
        :param area: list
        :param blocksize: number of returned rows
        :return: list
        """

        try:

            dim_service = DimensionService(self._connection)
            element_service = ElementService(self._connection)

            database = cube.database

            # get cube dimensions
            cube_dims = cube.dimensions

            # get data
            service_method = "/cell/export"
            payload = dict()
            payload["database"] = database.id
            payload["cube"] = cube.id

            payload["base_only"] = +base_only
            payload["use_rules"] = +use_rules
            payload["skip_empty"] = 2 if ignore_empty else 0
            payload["blocksize"] = blocksize

            # manage condition
            if condition is not None:
                param_condition = []
                for condition_item in condition:
                    key, value = next(iter(condition_item.items()))
                    value_param = f'"{value}"' if isinstance(value, str) else value
                    param_condition.append(f"{key}{value_param}")

                payload["condition"] = condition_operator.join(param_condition)

            # analyse each coordinates item
            coordinates = area.copy()
            for area_id, area_ele in enumerate(area):
                dim = cube_dims[area_id]
                # list : concatenate with ":"
                if isinstance(area_ele, list):
                    coordinates[area_id] = ':'.join(area_ele)
                # all
                if area_ele == "*":
                    coordinates[area_id] = area_ele
                # bases of the element
                elif isinstance(area_ele, str) and base_only:
                    # get dimension
                    dim_obj = dim_service.get(database=database, dimension_name=dim)

                    # get elements
                    bases = element_service.get_base_elements(dimension=dim_obj, element=area_ele)
                    bases_names = [x['name_element'] for x in bases.values()]
                    coordinates[area_id] = ':'.join(bases_names)
                else:
                    pass

            out_virtual_coords = list()

            virtual_coords = dict()

            # change the format of the virtual coordinates : {("dim_name","attribute"):"value"}
            # append the virtual dimensions if at least one virtual dimension is defined
            if virtual is not None and len(virtual) > 0:

                for virtual_dim, virtual_attr_pairs in virtual.items():
                    for virtual_attr, virtual_value in virtual_attr_pairs.items():
                        virtual_coords[(virtual_dim, virtual_attr)] = virtual_value

                for cube_dim in cube_dims:

                    # only for virt dims
                    if isinstance(cube_dim, tuple):
                        virt_dim = cube_dim[1]
                        virt_dim_value = virtual_coords.get(cube_dim)

                        if virt_dim_value is not None:
                            if isinstance(virt_dim_value, list):
                                virt_dim_value = ":".join(virt_dim_value)

                            out_virtual_coords.append(virt_dim_value)
                        else:
                            out_virtual_coords.append(virt_dim)

            coordinates = coordinates + out_virtual_coords

            print(coordinates)

            payload["name_area"] = ",".join(coordinates)

            print("from method:")
            print(payload["name_area"])

            out = dict()

            # get dimensions with ids and names
            for dim in cube_dims:
                if isinstance(dim, tuple):
                    dim = "#_VIRTUAL_{}_ATTRIBUTE_{}".format(*dim)

                    # skip if no virtual. no need to query the elements
                    if virtual is None:
                        continue

                # create dim obj
                dim_as_dim = dim_service.get(database=database, dimension_name=dim)
                out[dim] = element_service.get_elements_by_id(dimension=dim_as_dim)
                dim_elements = out

            # iterating on the response payload (batch of 1000 per default)
            # the paging information seems to be wrong, thus using the next path record
            exported_rows = list()
            nb_of_calls = 0
            next_record = ""
            while next_record is not None:

                if next_record != '':
                    payload["path"] = ','.join(next_record)

                result_data = self._connection.request(service_method=service_method, payload=payload, header=False)
                nb_of_calls = nb_of_calls + 1

                if len(result_data) == 1 and result_data[0][0] == result_data[0][1] == '1000':
                    next_record = None
                else:
                    result_data.pop()

                    # iterate over the export result
                    for row in result_data:

                        value = row[2]
                        path = row[3]
                        type_cell = row[0]
                        path_list = path.split(",")
                        next_record = path_list

                        exported_columns = list()
                        for dim_element_id, dim_element_path in enumerate(path_list):
                            dim_path = cube_dims[dim_element_id]

                            if isinstance(dim_path, tuple):
                                if virtual_coords.get(dim_path) is None:
                                    continue
                                dim_path = "#_VIRTUAL_{}_ATTRIBUTE_{}".format(*dim_path)

                            element_name = dim_elements[dim_path][int(dim_element_path)]
                            exported_columns.append(element_name)

                        exported_columns.append(float(value) if type_cell == 1 else value)

                        exported_rows.append(exported_columns)

            if with_header:

                out_columns = []

                for cube_dim_column in cube_dims:
                    if isinstance(cube_dim_column, tuple):
                        if virtual_coords is not None and virtual_coords.get(cube_dim_column) is not None:
                            out_columns.append(cube_dim_column[1])
                    else:
                        out_columns.append(cube_dim_column)

                out_columns.append("Value")

                exported_rows.insert(0, out_columns)

            return exported_rows

        except JedoxPyException:
            raise

    def get_data_as_dataframe(self, cube: Cube, area: list, blocksize: int = 1000, base_only: bool = True,
                              ignore_empty: bool = False, use_rules: bool = False,
                              condition: list[dict] = None, condition_operator: Operator = Operator.AND,
                              virtual: dict = None, with_header: bool = True) -> 'pd.DataFrame':

        kwargs = locals()
        kwargs.pop("self")
        data = self.get_data_export(**kwargs)

        # get cube dimensions
        cube_dims = cube.dimensions

        df_columns = data.pop(0)

        df = pd.DataFrame(data=data, columns=df_columns)

        return df
    # header to True to get the list of the output columns

    def set_cell_data(self, value: float | int | str, cube: Cube, coordinates: Iterable[str],
                      splash_mode: SplashingTypes = SplashingTypes.SPLASH_MODE_NONE, holds: list[str] = None,
                      virtual: dict=None):

        payload = dict()

        database = cube.database

        payload["database"] = database.id
        payload["cube"] = cube.id

        cube_dims = cube.dimensions
        if virtual is None:
            cube_dims = [x for x in cube_dims if not isinstance(x, tuple)]

        # if a dict is passed : reorder by keys using the cube dimensions
        if isinstance(coordinates, dict):

            # check if missing keys
            missing_keys = [key for key in cube_dims if key not in coordinates]
            extra_keys = [key for key in coordinates if key not in cube_dims]
            if len(missing_keys) > 0:
                raise JedoxPyException(f"Error, the following keys are missing: {",".join(missing_keys)}")
            elif len(extra_keys) > 0:
                raise JedoxPyException(f"Error, the following keys are too much: {",".join(extra_keys)}")
            else:
                coordinates = list({key: coordinates[key] for key in cube_dims}.values())

        payload["name_path"] = ",".join(coordinates)
        payload["value"] = f"{splash_mode.value}{value}" if not isinstance(value, str) else value

        # set mode to 1 for splashing
        payload["mode"] = 1

        if holds is not None:

            dim_service = DimensionService(self._connection)
            element_service = ElementService(self._connection)

            # get elements and ids
            out = dict()
            # get dimensions with ids and names
            for dim in cube_dims:
                # create dim obj
                dim_as_dim = dim_service.get(database=database, dimension_name=dim)
                out[dim] = element_service.get_elements_by_name(dimension=dim_as_dim)
                dim_elements = out

            locked_paths = list()
            for hold in holds:
                locked_path = list()
                for hold_coord_index, hold_coord_element in enumerate(hold):

                    if out.get(cube_dims[hold_coord_index], {}).get(hold_coord_element) is None:
                        raise JedoxPyException(
                            f"Element of the hold definition {hold_coord_element} not found in dimension {cube_dims[hold_coord_index]}")

                    locked_path.append(str(out.get(cube_dims[hold_coord_index], {}).get(hold_coord_element)))

                locked_paths.append(",".join(locked_path))

            locked_paths_string = ":".join(locked_paths)

            payload["locked_paths"] = locked_paths_string

        req = self._connection.request(service_method="/cell/replace", payload=payload)

        return req.get("status")

    def write_dataframe(self, df: pd.DataFrame, database: Database, cube: Cube, value_column: str = "#Value"):

        cube_service = CubeService(self._connection)
        dim_service = DimensionService(self._connection)
        element_service = ElementService(self._connection)

        # get cube columns
        cube_columns = cube.dimensions

        source_columns = df.columns

        # extract the value
        df_value_col = df[value_column]

        # extract and reorder the relevant columns
        df = df[cube_columns]
        df["Value"] = df_value_col

        # # for each dimension, get the ids
        # out = dict()
        # # get dimensions with ids and names
        # for dim in cube_columns:
        #     # create dim obj
        #     dim_as_dim = dim_service.get(database=database, dimension_name=dim)
        #     out[dim] = element_service.get_elements_by_name(dimension=dim_as_dim)
        #
        # elements_as_df = pd.DataFrame.from_dict(
        #     out, orient='index'
        # ).stack().reset_index()
        # elements_as_df.columns = ["dim", "name", "id"]
        # elements_as_df["id"] = elements_as_df["id"].astype(int)
        #
        # for dim in cube_columns:
        #     df = df.merge(
        #         elements_as_df[elements_as_df['dim'] == dim][['name', 'id']],
        #         how='left',
        #         left_on=dim,
        #         right_on='name'
        #     ).drop(columns=['name'])
        #
        #     df = df.drop(columns=[dim])
        #     df = df.rename(columns={'id': dim})

        df["Value"] = df.pop("Value")

        df["concat"] = df[cube_columns].astype(str).agg(",".join, axis=1)

        target_coords = ":".join(df['concat'])
        target_values = ":".join(df["Value"].astype(str))

        payload = dict()
        payload["database"] = database.id
        payload["cube"] = cube.id
        payload["name_paths"] = target_coords
        payload["values"] = target_values

        res = self._connection.request(service_method="/cell/replace_bulk", payload=payload)

        return df
