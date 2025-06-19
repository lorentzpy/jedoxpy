from enum import Enum


class TypeObject(Enum):
    NORMAL = 0
    SYSTEM = 1
    ATTRIBUTE = 2
    USER_INFO = 3


class DatabaseStatus(Enum):
    UNLOADED = 0
    LOADED = 1
    CHANGED = 2
    ERROR = 3


class TypeElement(Enum):
    NUMERIC = 1
    STRING = 2
    CONSOLIDATED = 4


class SortingForValues(Enum):
    ALL = 0
    BASE = 0x000020
    CONSO = 0x002000


class HierarchyFilterTypes(Enum):
    BASE = 0x0004
    CONSOLIDATED = 0x0008


class DataFilterCriteria(Enum):
    MIN = 0x0001
    MAX = 0x0002
    SUM = 0x0004
    AVERAGE = 0x0008
    ANY = 0x0010
    ALL = 0x0020
    STRING = 0x0040

class AttributeFilterValues(Enum):

    SEARCH_ONE = 0x01
    SEARCH_TWO = 0x02
    ADVANCED_FILTER = 0x10
    USE_REGEX = 0x20
    IGNORE_CASE = 0x40
    INHERIT_FROM_PARENT = 0x80


class SortingFilterValues(Enum):
    PARENTS_BELOW_CHILDREN = 0x000010
    NO_SORTING_CONSO = 0x000020
    SHOW_DUPLICATES_DIFFERENT_PARENT = 0x000040
    SHOW_WHOLE_HIERACHY = 0x000080
    POSITION_DEFAULT = 0x000100
    REVERSE_SORTING = 0x000200
    SORT_ON_LEVEL = 0x000400
    NO_TREE = 0x000800
    BUILD_TREE = 0x001000
    SORT_ONLY_CONSO = 0x002000
    SORT_ALL_LEVELS = 0x004000
    SHOW_DUPLICATES = 0x008000
    REVERSE_ORDERING = 0x010000
    LIMIT_ELEMENTS = 0x020000
    RETURN_ID_PATH = 0x080000
    SKIP_SORTING = 0x100000
    NO_RETURN_PATH = 0x200000
    RETURN_NAME_PATH = 0x400000
    INHERIT_SORTING_FILTER = 0x800000


class SortingCriteria(Enum):
    SORT_ON_DEFINITION = 0x000000
    SORT_ON_NAME = 0x000001
    SORT_ON_VALUE = 0x000002
    SORT_ON_ATTRIBUTE = 0x000004
    SORT_ON_ALIAS = 0x000008
    SORT_ON_CONSO = 0x040000


class PicklistTypes(Enum):
    HEAD = 0x08
    TAIL = 0x01
    MERGE = 0x02
    PRESELECT = 0x04
    PRESELECT_ORDER = 0x40


class SplashingTypes(Enum):
    SPLASH_MODE_NONE = ""
    SPLASH_MODE_DEFAULT = "#"
    SPLASH_MODE_DEFAULT_ADD = "##"
    SPLASH_MODE_SET = "!"
    SPLASH_MODE_ADD = "!!"
    SPLASH_MODE_SET_POPULATED = "!#"
    SPLASH_MODE_ADD_POPULATED = "!!#"


class DimensionType(Enum):
    NORMAL = 0
    SYSTEM = 1
    ATTRIBUTE = 2
    USER_INFO = 3
    SYSTEM_ID = 4
    VIRTUAL_ATTRIBUTE = 5


class RuleTemplateType(Enum):
    NO_RULE_TEMPLATE = ""
    DIMENSION_ELEMENT_LIKE = "Dimension element like"
    DIMENSION_ELEMENT_LIKE_LIST = "Dimension element  like (list)"
    DIMENSION_ELEMENT_LIKE_ATTRIBUTE = "Dimension element like attribute"
    DIMENSION_ELEMENT_LIKE_ATTRIBUTE_LIST = "Dimension element like attribute (list)"
    ACTUAL_MONTHS = "Actual months"
    STATIC_FORMAT_STRING = "Static format string"
    DIMENSION_FORMAT_STRING = "Dimension format string"
    KPI_CALCULATION = "KPI calculation"
    KPI_CALCULATION_BY_VERSION = "KPI calculation (by Version)"
    ATTRIBUTE_LIKE = "Attribute like"
    INITIAL_MONTHS = "Initial months"
    GLOBAL_SUBSET_ELEMENT = "Global Subset element"
    GLOBAL_SUBSET_ELEMENT_LIST = "Global Subset element (list)"
    DIMENSION_ELEMENT_LIKE_GROUP_BY_ONE_ATTRIBUTE_VALUE = "Dimension element like group by one attribute value"
    DIMENSION_ELEMENT_LIKE_GROUP_BY_TWO_ATTRIBUTE_VALUES = "Dimension element like group by two attribute values"
    DIMENSION_ELEMENT_LIKE_GROUP_BY_THREE_ATTRIBUTE_VALUES = "Dimension element like group by three attribute values"


class DimensionLoadModes(Enum):
    CREATE = "create"
    UPDATE = "update"
    ADD = "add"
    INSERT = "insert"
    DELETE = "delete"


class Operator(str, Enum):
    AND = "and"
    OR = "or"

class DimensionProperty(str, Enum):
    DESCRIPTION = "Description"
    TOTAL = "TotalElement"
    NA = "NAElement"
    DEFAULT_READ = "DefaultReadElement"
    DEFAULT_WRITE = "DefaultWriteElement"
    DEFAULT_PARENT = "DefaultParentElement"

class ExtractionMode(Enum):
    ONLY_BASES = "onlyBases"
    ROOT_TO_BASES = "rootToBases"
    ROOT_TO_NODES = "rootToNodes"
    ROOT_TO_CONSOLIDATES = "rootToConsolidates"
    NODES_TO_BASES = "nodesToBases"
    ONLY_CHILDREN = "onlyChildren"
    ONLY_NODES = "onlyNodes"
    ONLY_ROOTS = "onlyRoots"
