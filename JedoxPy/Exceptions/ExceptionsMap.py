from JedoxPy.Exceptions.Exceptions import (JedoxPyAlreadyExistsException,
                                           JedoxPyNotFoundException,
                                           JedoxPyInvalidNameException,
                                           JedoxPyNotDeletableException,
                                           JedoxPyNotRenamableException,
                                           JedoxPyNotChangableException)

# manage not found / already exists / invalid name / not alterable exceptions related to objects
OBJECTS_EXCEPT_MAP = {
                2001: ("database", JedoxPyNotFoundException),
                3002: ("dimension", JedoxPyNotFoundException),
                4004: ("element", JedoxPyNotFoundException),
                5000: ("cube", JedoxPyNotFoundException),
                8002: ("rule", JedoxPyNotFoundException),
                2005: ("database", JedoxPyAlreadyExistsException),
                3005: ("dimension", JedoxPyAlreadyExistsException),
                4002: ("element", JedoxPyAlreadyExistsException),
                5008: ("cube", JedoxPyAlreadyExistsException),
                2000: ("database", JedoxPyInvalidNameException),
                3003: ("dimension", JedoxPyInvalidNameException),
                4006: ("element", JedoxPyInvalidNameException),
                5001: ("cube", JedoxPyInvalidNameException),
                2006: ("database", JedoxPyNotDeletableException),
                5009: ("cube", JedoxPyNotDeletableException),
                3007: ("dimension", JedoxPyNotDeletableException),
                4010: ("element", JedoxPyNotDeletableException),
                2007: ("database", JedoxPyNotRenamableException),
                5010: ("cube", JedoxPyNotRenamableException),
                3008: ("dimension", JedoxPyNotRenamableException),
                4011: ("cube", JedoxPyNotRenamableException),
                3004: ("dimension", JedoxPyNotChangableException),
                4012: ("element", JedoxPyNotChangableException),
                5010: ("cube", JedoxPyNotChangableException)
            }