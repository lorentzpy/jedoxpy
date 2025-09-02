class JedoxPyException(Exception):

    def __init__(self, error_code: int = None, error_msg: str=None, param = None):
        self.error_code = error_code
        self.error_msg = error_msg
        self.param = param
        err = f"[{error_code}] " if error_code else ""
        msg = f"{err}{error_msg}"
        msg += f"({param})" if param is not None else ""
        super().__init__(msg)


class JedoxPySubsetException(Exception):

    def __init__(self, className, message):
        self.className = className
        self.message = message

    def __str__(self):
        return f"{self.message}. Class: {self.className}"


class JedoxPyRequestException(JedoxPyException):

    def __init__(self, error_code: int, error_msg: str, param):
        self.error_code = error_code
        self.error_msg = error_msg
        self.param = param

class JedoxPyAuthException(JedoxPyException):
    pass

class JedoxPyAlreadyExistsException(JedoxPyException):

    def __init__(self, jedox_object_type=None, jedox_object=None, error_code=None, custom_message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        if not custom_message:
            error_msg = f"{jedox_object_type.capitalize()} {jedox_object} already exists"
        else:
            error_msg = custom_message
        super().__init__(error_code=error_code, error_msg=error_msg)


class JedoxPyNotFoundException(JedoxPyException):

    def __init__(self, jedox_object_type=None, jedox_object=None, error_code=None, custom_message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        if not custom_message:
            error_msg = f"{jedox_object_type} {jedox_object} was not found"
        else:
            error_msg = custom_message
        super().__init__(error_code=error_code, error_msg=error_msg)


class JedoxPyInvalidNameException(JedoxPyException):

    def __init__(self, jedox_object_type=None, jedox_object=None, error_code=None, custom_message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        if not custom_message:
            error_msg = f"invalid name {jedox_object} for {jedox_object_type}"
        else:
            error_msg = custom_message
        super().__init__(error_code=error_code, error_msg=error_msg)


class JedoxPyNotDeletableException(JedoxPyException):

    def __init__(self, jedox_object_type, jedox_object, error_code, message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        super().__init__(error_code=error_code, error_msg=f"{jedox_object_type.capitalize()} {jedox_object} cannot be deleted", param=None)


class JedoxPyNotRenamableException(JedoxPyException):

    def __init__(self, jedox_object_type, jedox_object, error_code, message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        super().__init__(error_code=error_code, error_msg=f"{jedox_object_type.capitalize()} {jedox_object} cannot be renamed", param=jedox_object)


class JedoxPyDatabaseErrorException(JedoxPyException):
    pass


class JedoxPyDimensionErrorException(JedoxPyException):

    def __init__(self, error_code, error_msg, param_info):
        super().__init__(error_code=error_code, error_msg=error_msg, param=param_info)


class JedoxPyNotChangeableException(JedoxPyException):

    def __init__(self, jedox_object_type, jedox_object, error_code, message=None):
        self.jedox_object_type = jedox_object_type
        self.jedox_object = jedox_object
        super().__init__(error_code=error_code, error_msg=f"{jedox_object_type.capitalize()} {jedox_object} cannot be altered", param=jedox_object)


class JedoxPyAuthorizationException(JedoxPyException):

    def __init__(self, error_code, error_msg, param_info):
        super().__init__(error_code=error_code, error_msg=error_msg, param=param_info)

class JedoxPyServerNotReachable(JedoxPyException):
    def __init__(self, error_code, error_msg, param_info):
        super().__init__(error_code=404, error_msg="Server is not reachable", param=None)