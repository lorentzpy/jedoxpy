from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Objects.Subset import Subset
from JedoxPy.Exceptions.Exceptions import JedoxPyException, JedoxPyNotFoundException

class SubsetService():

    def __init__(self, connection: ConnectionService):

        self._connection = connection

    def execute_subset(self, subset: Subset, size_only=False) -> dict:

        conn = self._connection

        view_axes = f'"{subset.subset_id}";"";"";0'

        view_subset = f'"{subset.subset_id}";"{subset.dimension.name}";'
        view_subset_list = []
        for filter in subset.filters:
            view_subset_list.append(filter.generate_view_subset())

        view_subset += ";".join(view_subset_list)

        payload = dict()
        payload["name_database"] = subset.database.name
        payload["squash_list"]=0
        payload["view_subsets"] = view_subset
        payload["view_axes"] = view_axes
        payload["mode"] = 1540
        #257

        response = conn.request(service_method="/view/calculate", payload=payload, header=False)

        response.pop(0)

        response_body = response

        if ["[Errors]"] in response:
            # get error code
            error_section_pos = response.index(["[Errors]"])
            error_section = response[error_section_pos+2]
            error_code = int(error_section[0])
            error_msg = error_section[1]
            raise JedoxPyException(error_code=error_code, error_msg=error_msg)

        elements=dict()
        properties = ["name_element","position","level","indent","depth","type","number_parents","parents","number_children","children","weights"]
        for item in response_body:
            if len(item)!=0:
                id = item.pop(0)
                item += [None] * ( 11 - len(item) )
                elements[id] = dict(zip(properties, item))

        return elements


    def execute_subset_get_names(self, subset: Subset) -> list:

        elements = self.execute_subset(subset=subset)
        element_names = list()

        for element in elements:
            element_names.append(element[1])

        return element_names
