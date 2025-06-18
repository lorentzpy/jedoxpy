from JedoxPy.Services.ConnectionService import ConnectionService
from JedoxPy.Objects.Cube import Cube
from JedoxPy.Objects.Rule import Rule
from JedoxPy.Objects.Enums import RuleTemplateType
import json

class RulesService:

    def __init__(self, connection: ConnectionService):
        self._connection = connection

    def get_list(self,
            cube: Cube,
            show_ip_protection: bool=False,
            regular: bool=True,
            rule_templates: bool=True,
            generated: bool=False,
            use_identifier: bool=False) -> list:

        service_method = "/cube/rules"

        payload = dict()
        payload["database"] = cube.database.id
        payload["cube"] = cube.id
        payload["show_protection"] = +show_ip_protection
        payload["use_identifier"] = +use_identifier

        rules = self._connection.request(service_method=service_method, payload=payload, header=True)

        rules_out = list()
        for rule in rules:
            if regular and rule.get("query") == "" and rule.get("template_rule") is None:
                rule_obj = Rule.from_dict(rule)
                rules_out.append(rule_obj)
            if rule_templates and rule.get("query") != "" and rule.get("template_rule") is None:
                rule_obj = Rule.from_dict(rule)
                rules_out.append(rule_obj)
            if generated and rule.get("template_rule") is not None:
                rule_obj = Rule.from_dict(rule)
                rules_out.append(rule_obj)

        return rules_out

    def get_number_of_rules(self, cube: Cube) -> int:

        return len(self.get_list(cube=cube))

    def get_rule_by_id(self, cube: Cube, rule_id: int) -> Rule:

        payload = dict()
        payload["database"] = cube.database.id
        payload["cube"] = cube.id
        payload["rule"] = rule_id

        req = self._connection.request(service_method="/rule/info", payload=payload, header=True)

        rule = Rule.from_dict(req)

        rule.set_cube(cube=cube)

        return rule


    def get_rule_by_def(self, cube: Cube, rule: str) -> Rule:

        # search for the rule def among the whole list of rules
        rules = self.get_list(cube=cube, generated=False)

        id = None
        for rule_item in rules:
            if rule_item.get("rule_string") == rule:
                id = rule_item.get("rule")

        if id is None:
            return "Rule not found!"

        return self.get_rule_by_id(cube=cube, rule_id=id)

    def create(self,
               cube: Cube,
               definition: str,
               activate:bool=True,
               comment: str=None,
               position: int=0,
               #rule_template: RuleTemplateType=RuleTemplateType.NO_RULE_TEMPLATE,
               rule_template_query: dict=None):

        payload=dict()
        payload["database"] = cube.database.id
        payload["cube"] = cube.id
        payload["definition"] = definition
        payload["activate"] = +activate
        payload["comment"] = comment
        payload["position"] = position

        if rule_template_query is not None:
            payload["source"] = json.dumps(rule_template_query)

        req = self._connection.request("/rule/create", payload=payload, header=False)

        return req

    def move(self, rule: Rule, position: float):

        payload=dict()
        payload["database"] = rule.cube.database.id
        payload["cube"] = rule.cube.id
        payload["rule"] = rule.rule_id
        payload["position"] = position

        req = self._connection.request(service_method="/rule/modify", payload=payload, header=False)


    def toggle_state(self, rule: Rule):

        payload = dict()
        payload["database"] = rule.cube.database.id
        payload["cube"] = rule.cube.id
        payload["rule"] = rule.rule_id
        payload["activate"] = 2

        req = self._connection.request(service_method="/rule/modify", payload=payload, header=False)

    def activate(self, rule: Rule):

        payload = dict()
        payload["database"] = rule.cube.database.id
        payload["cube"] = rule.cube.id
        payload["rule"] = rule.rule_id
        payload["activate"] = +(True)

        req = self._connection.request(service_method="/rule/modify", payload=payload, header=False)
