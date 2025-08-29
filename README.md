# Jedox Python Client

Python client for [Jedox](https://www.jedox.com/).
* Uses the HTTP/1.1 OLAP API of Jedox.
* Cloud-compatible
* Developed using the last on prem-version: some of the latest functionalities are missing

* This is still a beta version! I've been working alone on the project, and this is my very first Python project so I'm open for criticism and advice. Feel free to contribute!

## Trademark notice

This project provides a Python API to interact with Jedox software.

Jedox is a registered trademark of Jedox AG.  
This project is an independent work and is **not affiliated with, endorsed by, or sponsored by Jedox AG** in any way.

All trademarks and brand names mentioned are the property of their respective owners.

## Usage

Basic call
```
from JedoxPy import JedoxService
host = "localhost" # or any cloud olap address, e.g olap.myinstance.cloud.jedox.com
port = 7777
username = admin
password = admin
ssl = False

with JedoxService(host=host, port=port, username=user, password=password, ssl=ssl) as js:
    version = js.connection.get_version()
    print(version)

# or without with:
js = JedoxService(host=host, port=port, username=user, password=password, ssl=ssl)

js.connect()
version = js.connection.get_version()
print(version)
js.disconnect()
```

List cubes
```
with JedoxService(host=host, port=port, username=user, password=password, ssl=ssl) as js:
    database = js.databases.get(name="Demo") # returns a Database object
    cubes = js.databases.get_cubes(database=database) # returns a list of Cube objects
```





