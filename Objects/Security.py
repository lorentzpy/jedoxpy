

class SecurityObject:
    def __init__(self, id: int = None, name: str = None, description: str = "", inactive: bool = None):
        self.id = id
        self.name = name
        self.description = description
        self.inactive = inactive

    @classmethod
    def fromdict(cls, security_obj_as_dict: dict):

        kwargs = {
            "id": int(security_obj_as_dict.get("id")) if not None else None,
            "name": security_obj_as_dict.get("name"),
            "description":security_obj_as_dict.get("description") if not None else "",
            "inactive": True if security_obj_as_dict.get("inactive") == '1' else False
        }

        return kwargs

        #return cls(id=id, name=name, description=description, inactive=inactive)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name} (id: {self.id}) ; {self.description} ; inactive: {self.inactive}"

class User(SecurityObject):

    #def __init__(self, id: int, name: str, full_name: str, description: str, inactive: bool, last_login: int):
    def __init__(self, full_name: str, last_login: int = 0, **kwargs):

        super().__init__(**kwargs)
        self.full_name = full_name
        self.last_login = last_login
        self.groups = None

    def __str__(self):
        base_infos = super().__str__()

        return f"{base_infos} ; full name: {self.full_name} ; last login: {self.last_login} ; groups: {self.groups}"
    @classmethod
    def fromdict(cls, user_as_dict: dict):

        # get common arguments
        base_args = super().fromdict(user_as_dict)

        # append specific arguments
        base_args.update({
            "full_name": user_as_dict.get("fullName"),
            "last_login": user_as_dict.get("last_login", 0)
        })

        return cls(**base_args)

    def set_groups(self, groups: list):

        self.groups = groups

class Group(SecurityObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roles = None

    def __str__(self):
        base_infos = super().__str__()

        return f"{base_infos} ; roles: {self.roles}"

    @classmethod
    def fromdict(cls, group_as_dict: dict):
        base_args = super().fromdict(group_as_dict)

        return cls(**base_args)

    def set_roles(self, roles: list):

        self.roles = roles


class Role(SecurityObject):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.groups = None

    def __str__(self):
        base_infos = super().__str__()

        return f"{base_infos} ; groups: {self.groups}"

    @classmethod
    def fromdict(cls, role_as_dict: dict):
        # get common arguments
        base_args = super().fromdict(role_as_dict)

        return cls(**base_args)

    def set_groups(self, groups: list):
        self.groups = groups
