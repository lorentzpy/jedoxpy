from JedoxPy.Services.ConnectionService import ConnectionService

class SupervisionServerService:

    def __init__(self, connection: ConnectionService):

        self._connection = connection

    def get_info(self):

        req = self._connection.request(service_method="/svs/info")

        return req

    def restart(self):

        req = self._connection.request(service_method="/svs/restart", header=False)

        return req

    def stop(self):

        payload = dict()
        payload["mode"] = 1

        req = self._connection.request(service_method="/svs/restart", payload=payload, header=False)

        return req