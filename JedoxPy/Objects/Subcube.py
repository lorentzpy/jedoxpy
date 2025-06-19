from JedoxPy.Objects.Cube import Cube
from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Services.DimensionService import DimensionService
from JedoxPy.Services.ElementService import ElementService
from JedoxPy.Objects.Enums import ExtractionMode

# if modes is None: take base cells as default
class Subcube:

    def __init__(self, cube: Cube, area: list, area_virtual: dict=None, modes: list=None):

        self.cube = cube
        self.area = area
        self.area_virtual = area_virtual
        self.modes = modes
        self.processed_area = self.process_area(area)

    def process_area(self, area) -> str:

        dim_service = DimensionService(self.connection)
        element_service = ElementService(self.connection)

        database = self.cube.database
        cube_dims = self.cube.dimensions

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
            elif isinstance(area_ele, str) and self.modes is None:
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
        if self.area_virtual is not None and len(self.area_virtual) > 0:

            for virtual_dim, virtual_attr_pairs in self.area_virtual.items():
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

        return ",".join(coordinates)