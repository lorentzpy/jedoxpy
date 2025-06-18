from JedoxPy.Objects.Database import Database
from JedoxPy.Objects.Dimension import Dimension
from JedoxPy.Exceptions.Exceptions import JedoxPySubsetException
from JedoxPy.Objects.Enums import (PicklistTypes,
                                   HierarchyFilterTypes,
                                   SortingFilterValues,
                                   SortingCriteria,
                                   SortingForValues,
                                   DataFilterCriteria,
                                   AttributeFilterValues)

from JedoxPy.Objects.Cube import Cube

from abc import ABC, abstractmethod
from typing import List, Dict

import string, random

PICKLIST_FILTER = 0
HIERARCHY_FILTER = 1
ATTRIBUTE_FILTER = 2
TEXT_FILTER = 3
DATA_FILTER = 4
SORTING_FILTER = 5
STORED_SUBSET = 6

class Filter(ABC):
    @abstractmethod
    def generate_view_subset(self)->str:
        pass
class HierarchyFilter(Filter):

    def __init__(self,
                 hierarchy_type:HierarchyFilterTypes=None,
                 element: str=None,
                 direction:str=None,
                 exclusive: bool=False,
                 filter_type: HierarchyFilterTypes = None,
                 level_from: int=None,
                 level_to: int=None,
                 relative: bool=None):

        self.hierarchy_type=hierarchy_type
        self.element=element
        self.direction=direction
        self.exclusive=exclusive
        self.filter_type=filter_type
        self.level_from=level_from
        self.level_to=level_to
        self.relative=relative

    def generate_flag_string(self):

        flag_mapping = {
            ("below", False): 0x0001,
            ("below", True): 0x0002,
            ("above", True): 0x0200,
            ("above", False): 0x0400,
            ("siblings", True): 0x2000,
            ("siblings", False): 0x4000,
        }

        #flag = 0x0008
        flag = 0
        if self.filter_type is not None:
            flag += self.filter_type.value

        flag += flag_mapping[(self.direction, self.exclusive)]

        if self.hierarchy_type is not None:
            flag += self.hierarchy_type.value

        return flag

    def generate_view_subset(self) ->str:

        revolve_count=""
        revolve_name=""

        flag = self.generate_flag_string()
        element_string = self.element

        view_subset = f"{HIERARCHY_FILTER};{flag};1;\"{element_string}\";{(self.level_from or "")};{(self.level_to or "")};{revolve_count};{revolve_name}"

        return view_subset

class TextFilter(Filter):

    def __init__(self, regexes: list=None, use_perl: bool=False, use_name_not_alias: bool=False, ignore_case: bool=False):

        self.use_perl = use_perl
        self.use_name_not_alias = use_name_not_alias
        self.ignore_case = ignore_case
        self.regexes = regexes

    def generate_flag_string(self):

        flag = (+self.use_perl * 0x02) + (+self.use_name_not_alias * 0x04) + (+self.ignore_case * 0x08)

        return str(flag)

    def generate_view_subset(self):

        flag = self.generate_flag_string()
        regex_string = ":".join(self.regexes)

        view_subset=f"{TEXT_FILTER};{flag};{regex_string}"

        return view_subset

class PicklistFilter(Filter):

    def __init__(self, elements: list, behavior: PicklistTypes):

        self.elements = elements
        self.behavior = behavior

    def generate_flag_string(self):

        flag = self.behavior.value

        return str(flag)

    def generate_view_subset(self):
        flag = self.generate_flag_string()
        element_string = ":".join(self.elements)

        view_subset = f"{PICKLIST_FILTER};{flag};{element_string}"

        return view_subset

# class AttributeFilter(Filter):
#
#     def __init__(self, ):

class DataFilter(Filter):

    def __init__(self,
                 cube: Cube,
                 dimension: Dimension,
                 area: list,
                 criteria: DataFilterCriteria,
                 operator1: str,
                 value1: float = 0,
                 operator2: str = "",
                 value2: float = 0,
                 top: int = ""):

        self.cube = cube
        self.dimension = dimension
        self.area = area
        self.criteria = criteria
        self.operator1 = operator1
        self.value1 = value1
        self.operator2 = operator2
        self.value2 = value2
        self.top = top

    def generate_flag_string(self):

        flag = self.criteria.value
        return str(flag)

    def generate_view_subset(self) ->str:
        use_string = 1 if self.criteria == DataFilterCriteria.STRING else 0
        flag = self.generate_flag_string()
        coords = []
        for dim_element in self.area:
            if isinstance(dim_element, list):
                coords.append(":".join(f'"{dim_element_element}"' for dim_element_element in dim_element))
            else:
                coords.append(f'"{dim_element}"')

        area_quoted = map(lambda n: f"{n}" if n!="" else "", coords)
        view_subset =  (f'{DATA_FILTER};{flag};"{self.cube.name}";{use_string};"{self.operator1}";{self.value1};"{self.operator2}";{self.value2};'
                       f'6;{';'.join(area_quoted)}'
                       f';;;-1;8;0')


        return view_subset

class SortingFilter(Filter):

    def __init__(self,
                 sorting_criterium: SortingCriteria = SortingCriteria.SORT_ON_DEFINITION,
                 parent_below_children: bool=False,
                 sort_for_level: SortingForValues = SortingForValues.ALL,
                 sort_at_level: int=0,
                 limit_elements: int=0,
                 start_with_pos: int=0,
                 attribute_name: str=None,
                 show_duplicates: bool=True,
                 reverse: bool=False):

        # sorting over attribute but no attribute provided
        if sorting_criterium == SortingCriteria.SORT_ON_ATTRIBUTE and attribute_name is None:

            raise JedoxPySubsetException(self.__class__.__name__, "Sorting criterium selected, but no attribute provided")

        self.sorting_criterium = sorting_criterium
        self.parent_below_children = parent_below_children
        self.sort_for_level = sort_for_level
        self.sort_at_level = sort_at_level

        if limit_elements>=0:
            self.limit_elements = limit_elements
        else:
            self.limit_elements = 2147483647

        self.start_with_pos = start_with_pos
        self.attribute_name = attribute_name
        self.show_duplicates = show_duplicates
        self.reverse = reverse

    def generate_flag_string(self) ->str:

        # start with the sorting criterium
        flag = self.sorting_criterium.value

        flag += +(self.show_duplicates) * SortingFilterValues.SHOW_DUPLICATES.value

        # those options seem to be default ones => they are not
        # flag += SortingFilterValues.SHOW_WHOLE_HIERACHY.value
        # flag += SortingFilterValues.POSITION_DEFAULT.value

        flag += SortingFilterValues.SHOW_WHOLE_HIERACHY.value

        # parent below children
        flag += (+self.parent_below_children) * SortingFilterValues.PARENTS_BELOW_CHILDREN.value
        # sort for level
        #flag += self.sort_for_level.value

        flag += +(self.reverse) * SortingFilterValues.REVERSE_SORTING.value
        # append the return_name_path, so that the returned structure matches with the one of /element/info
        #bflag += SortingFilterValues.RETURN_ID_PATH.value

        return flag

    def generate_view_subset(self):

        flag = self.generate_flag_string()
        #flag = "33152"


        # TO DO: indent dynamic
        # 2147483647 : voluntarily big number to take all ?
        view_subset = f"{SORTING_FILTER};{flag};1;{self.attribute_name or ""};{self.sort_at_level};{self.limit_elements};{self.start_with_pos}"

        return view_subset

class StoredSubset(Filter):

    def __init__(self, stored_subset_name: str, is_global: bool=True, variables: List[Dict[str,str]] = []):

        self.stored_subset_name = stored_subset_name
        self.is_global = is_global
        self.variables = variables

    def generate_view_subset(self):

        view_subset_terms = []
        view_subset_terms.append(f"{STORED_SUBSET}")
        view_subset_terms.append(f'"{self.stored_subset_name}"')
        view_subset_terms.append(str(+self.is_global))
        view_subset_terms.append(str(len(self.variables)))

        if len(self.variables) > 0:
            format_variables = []
            for variable in self.variables:
                format_variables.append(list(variable.keys())[0] + "=" + list(variable.values())[0])

            variables_string = ";".join(format_variables)

            view_subset_terms.append(variables_string)

        view_subset = ";".join(view_subset_terms)

        return view_subset

class AttributeFilter(Filter):

    # attributes format : {"attr1":["value1","value2"...], "attr2":["value1","value2"...]}
    # translations format : {"attr1":True, "attr2":False...}
    def __init__(self, attr1_name: str=None, attr2_name: str=None, attribute_filters: dict=None, use_regex: bool=False, ignore_case: bool=False, translations: dict=None):

        self.attr1_name = attr1_name or ""
        self.attr2_name = attr2_name or ""
        self.attribute_filters = attribute_filters
        self.use_regex = use_regex
        self.ignore_case = ignore_case
        self.translations = translations

    def generate_flag_string(self) -> int:

        flag = 0
        # regex
        flag += +(self.use_regex) * AttributeFilterValues.USE_REGEX.value

        # ignore case
        flag += +(self.ignore_case) * AttributeFilterValues.IGNORE_CASE.value

        return flag

    def generate_view_subset(self) -> str:

        flag = self.generate_flag_string()

        column_length = max(len(v) if isinstance(v, list) else 1 for v in self.attribute_filters.values())+1

        attribute_filter_list = []
        for attribute_filter_name, attribute_filter_value in self.attribute_filters.items():
            attribute_filter_list.append(f'"{attribute_filter_name}"')
            if isinstance(attribute_filter_value, list):
                for attribute_filter_value_item in attribute_filter_value:
                    attribute_filter_list.append(f'"{attribute_filter_value_item}"')
            else:
                attribute_filter_list.append(f'"{attribute_filter_value}"')

        attribute_filter_string = ":".join(attribute_filter_list)

        translations = self.translations or {}

        translations_string = ",".join(list({key: str(int(translations.get(key, False))) for key in self.attribute_filters}.values()))

        view_subset = f"{ATTRIBUTE_FILTER};{flag};{self.attr1_name};{self.attr2_name};{column_length}:{translations_string};{attribute_filter_string};8;0"

        return view_subset

class Subset:

    def __init__(self, connection, dimension: Dimension):

        self.connection = connection
        self.database = dimension.database
        self.dimension = dimension
        self.filters = []

        alphabet = string.ascii_lowercase + string.digits
        self.subset_id = {''.join(random.choices(alphabet, k=16))}

    def add_filter(self, filter: Filter):

        self.filters.append(filter)

