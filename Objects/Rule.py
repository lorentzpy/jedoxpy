from JedoxPy.Objects.Cube import Cube

class Rule:

    def __init__(self,
                 rule_id: int = None,
                 rule_def: str=None,
                 rule_comment: str=None,
                 rule_timestamp: int=None,
                 rule_active: bool=None,
                 rule_position: float=None,
                 rule_query: str=None,
                 rule_template_id: int=None
                 ):

        self.rule_id = rule_id
        self.rule_def = rule_def
        self.rule_comment = rule_comment
        self.rule_timestamp = rule_timestamp
        self.rule_active = rule_active
        self.rule_position = rule_position
        self.rule_query = rule_query
        self.rule_template_id = rule_template_id

    def __repr__(self):
        return ("Rule(rule_id={},rule_def={},rule_comment={},rule_timestamp={},rule_active={},rule_position={},"
                "rule_query={},rule_template_id={}").format(self.rule_id,
                                              self.rule_def,
                                              self.rule_comment,
                                              self.rule_timestamp,
                                              self.rule_active,
                                              self.rule_position,
                                              self.rule_query,
                                              self.rule_template_id
                                              )

    def __str__(self):
        return (f"Object {self.__class__.__name__} in database {self.cube.database.name} (id {self.cube.database.id}). "
                f"Cube: {self.cube.name} "
                f"Definition: {self.rule_def} ; "
                f"Rule id: {self.rule_id} "
                f"Rule state: {self.rule_active}"
                )

    @classmethod
    def from_dict(cls, rule_as_dict: dict) -> 'Rule':
        rule_id = rule_as_dict.get("rule")
        rule_string = rule_as_dict.get("rule_string")
        rule_comment = rule_as_dict.get("comment")
        rule_timestamp = rule_as_dict.get("rule_timestamp")
        rule_active = rule_as_dict.get("active")
        rule_position = rule_as_dict.get("position")
        rule_query = rule_as_dict.get("query")
        rule_template_id = rule_as_dict.get("template_rule")

        return cls(rule_id=rule_id,
                   rule_def=rule_string,
                   rule_comment=rule_comment,
                   rule_timestamp=rule_timestamp,
                   rule_active=rule_active,
                   rule_position=rule_position,
                   rule_query=rule_query,
                   rule_template_id=rule_template_id
                   )

    def set_cube(self, cube: Cube):

        self.cube = cube