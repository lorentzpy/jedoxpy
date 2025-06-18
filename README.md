# Jedox Python Client

Python client for [Jedox](https://www.jedox.com/).
* Uses the HTTP/1.1 OLAP API of Jedox.
* Cloud-compatible

* This is still a beta version. I've been working alone on the project, and this is my very first Python project so I'm open for criticism :-). I know Jedox very well, and Python a bit

## Usage

Basic call
```
from JedoxPy import JedoxService
host = "localhost" # or any cloud olap address
port = 7777
username = admin
password = admin

with JedoxService(host=host, port=port, username=user, password=password, ssl=ssl) as js:
    version = js.connection.get_version()
    print(version)
```

List cubes
```
with JedoxService(host=host, port=port, username=user, password=password, ssl=ssl) as js:
    database = js.databases.get(name="Demo") # returns a Database object
    cubes = js.databases.get_cubes(database=database) # returns a list of Cube objects
```
