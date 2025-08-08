import requests
from requests import Response

from JedoxPy.Utils.CSVParser import CSVParser
from JedoxPy.Exceptions.Exceptions import *
from JedoxPy.Exceptions.ExceptionsMap import OBJECTS_EXCEPT_MAP
from JedoxPy.Objects.Database import Database
from typing import List
import re


def check_response(response: Response):

    if not response.ok:

        error_values = CSVParser.parse(csv_data=response.text, header=False)
        header_error = ["error_code", "error_message", "error_message_alt", "param_name"]
        error_dict = dict(zip(header_error, error_values))

        print("error_values:", error_values)
        print("error_dict:", error_dict)

        try:
            error_code = int(error_dict.get("error_code"))
        except (TypeError, ValueError):
            error_code = None

        param_info = error_dict.get("param_name", "")
        param = ""
        if param_info:
            match = re.search(r"value\s+'([^']+)'", param_info)
            param = match.group(1) if match else None


        # match alternate return message for System objects
        DIM_OBJECT_MAP = {
            "#_USER_":"User",
            "#_GROUP_":"Group",
            "#_ROLE_":"Role"
        }

        match_alternate = re.search(r"element '(.*)' cannot be deleted from (.*)", error_dict["error_message_alt"])

        if error_code in OBJECTS_EXCEPT_MAP:

            obj_type, exception_class = OBJECTS_EXCEPT_MAP.get(error_code, None)
            if match_alternate:
                object_name = match_alternate.group(1)
                obj_type = DIM_OBJECT_MAP[match_alternate.group(2)]

            raise exception_class(jedox_object_type=obj_type,
                                  jedox_object=param,
                                  error_code=error_code)

        # manage other exceptions
        errors_map = {
            1009: JedoxPyAuthorizationException,
            1019: JedoxPyAuthException,
            2002: JedoxPyDatabaseErrorException,
            2003: JedoxPyDatabaseErrorException,
            3006: JedoxPyDimensionErrorException
        }

        exception_class = errors_map.get(error_code, JedoxPyException)

        if exception_class:
            raise exception_class(error_code,
                                  error_dict.get("error_message"),
                                  param_info)


class ConnectionService:

    def __init__(self, **kwargs):
        self.host = kwargs.get("host", None)
        self.port = kwargs.get("port", None)
        self.username = kwargs.get("username", None)
        self.password = kwargs.get("password", None)
        self.debug = kwargs.get("debug", False)
        self.ssl = kwargs.get("ssl", True)

        url_prefix = "http"
        if self.port is None:
            port = 80

        if self.ssl:
            url_prefix = f"{url_prefix}s"
            if self.port is None:
                port = 443

        self.root_url = f"{url_prefix}://{self.host}:{port}"

        self.session_id = None

        self.locale = kwargs.get("locale", None)

        self.connect(username=self.username, password=self.password, external_identifier=self.locale)

    def __str__(self):

        if self.session_id is None:
            return "Connection NOT established"
        else:
            return f"Connection established, sid: {self.session_id}"

    def connect(self, username: str, password: str, external_identifier: str = None):
        """ Connects to a Jedox server

        :param username
        :param username: str
        :param password: str
        :return: None
        """

        try:
            payload = dict()
            payload["user"] = username
            payload["extern_password"] = password

            payload["external_identifier"] = external_identifier

            result = self.request("/server/login", payload=payload, header=True)

            self.session_id = result["sid"]

        except JedoxPyRequestException as e:
            raise

    def disconnect(self):

        try:
            # /server/logout event
            payload = dict()
            payload["sid"] = self.session_id
            result = self.request(service_method="/server/logout", payload=payload, header=True)

        except JedoxPyRequestException:
            raise

    def request(self, service_method: str, payload=None, header=True):

        if payload is None:
            payload = dict()

        url = f"{self.root_url}{service_method}"

        if payload is None:
            payload = dict()

        if self.session_id is not None:
            payload["sid"] = self.session_id

        try:
            headers = dict()
            headers["Accept-Encoding"] = "identity, gzip"
            headers["Connection"] = "Keep-Alive"

            if self.debug:
                out = list()
                for k, v in payload.items():
                    out.append(f"{k}={v}")

                print(url + '?' + '&'.join(out))

            response = requests.post(url=url, data=payload)

            if self.debug:
                print(response.text)

            check_response(response=response)

            # manage errors
            if response.status_code == 200:
                return CSVParser.parse(csv_data=response.text, header=header, service_method=service_method,
                                       payload=payload)

        except JedoxPyRequestException as e:
            raise

    def get_databases(self,
                      show_normal: bool = True,
                      show_system: bool = False,
                      show_user_info: bool = False,
                      show_permission: bool = False,
                      show_counter: bool = False,
                      show_count_by_type: bool = False,
                      show_error: bool = False,
                      show_virtual: bool = False) -> List[Database]:

        try:

            from JedoxPy.Services.DatabaseService import DatabaseService

            payload = dict()
            payload["show_normal"] = +show_normal
            payload["show_system"] = +show_system
            payload["show_user_info"] = +show_user_info
            payload["show_permission"] = +show_permission
            payload["show_counter"] = +show_counter
            payload["show_count_by_type"] = +show_count_by_type
            payload["show_error"] = +show_error
            payload["show_virtual"] = +show_virtual

            result = self.request("/server/databases", payload=payload, header=True)

            db_service = DatabaseService(connection=self)

            db_objects = []
            for db in result:
                db_objects.append(db_service.get(name=db["name_database"]))

            return db_objects

        except JedoxPyRequestException:
            raise

    def get_databases_names(self,
                            show_normal: bool = True,
                            show_system: bool = False,
                            show_user_info: bool = False,
                            show_permission: bool = False,
                            show_counter: bool = False,
                            show_count_by_type: bool = False,
                            show_error: bool = False,
                            show_virtual: bool = False) -> list:

        databases = self.get_databases(show_normal, show_system, show_user_info, show_permission, show_counter,
                                       show_count_by_type, show_error, show_virtual)

        # force to a list if only 1 database
        if isinstance(databases, dict):
            databases = [databases]

        return [d.name for d in databases]

    def get_info(self,
                 show_counters: bool = True,
                 show_new_version: bool = True,
                 show_enckey: bool = False,
                 show_user_info: bool = True) -> dict:

        try:
            payload = dict()
            payload["show_counters"] = +show_counters
            payload["show_new_version"] = +show_new_version
            payload["show_enckey"] = +show_enckey
            payload["show_user_info"] = +show_user_info

            return self.request("/server/info", payload=payload, header=True)

        except JedoxPyRequestException:
            raise

    def get_version(self) -> str:

        try:
            payload = dict()
            result = self.request(service_method="/server/info", payload=payload, header=True)

            return f"{result["major_version"]}.{result["minor_version"]}.{result["patch_version"]}"

        except JedoxPyRequestException:
            raise

    def start_benchmark_test(self):
        # to be implemented
        pass
