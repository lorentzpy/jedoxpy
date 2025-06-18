import json
import os

class HeadersService:

    def __init__(self):

        current_dir = os.path.dirname(__file__)
        with open(os.path.join(current_dir, "headers.json"), "r") as header_source:
            self.api_headers = json.load(header_source)

    def get_header(self, call_name, payload=None):

        headers = self.api_headers[call_name]["base"].copy()

        # edge case for /dimension.info (the api delivers always dimension_token at the end)
        if call_name == "/dimension/info":
            # remove dimension_token...
            headers.remove("dimension_token")

        if payload:
            if "modifiers" in self.api_headers[call_name]:
                modifiers = self.api_headers[call_name]["modifiers"]
                for key, value in payload.items():
                    if key in modifiers and str(value) == list(self.api_headers[call_name]["modifiers"][key].keys())[0]:
                        additional_headers = modifiers[key].get(str(value))
                        headers.extend(additional_headers)

        if call_name == "/dimension/info":
            # add dimension_token again
            headers.append("dimension_token")

        return headers

    def is_single_result(self, call_name):

        # if the api call is listed in the json file
        if self.api_headers.get(call_name, False):
            # check whether the call returns a single result
            return self.api_headers.get(call_name).get("is_single_result", False)

        return False

        #return True if self.api_headers.get(call_name, False).get("is_single_result") else False

    def get_types(self, call_name):

        types = None
        if "types" in self.api_headers[call_name]:
            types = self.api_headers[call_name]["types"].copy()

        return types
