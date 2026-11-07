# 6.2 CSV, JSON, XML and settings files
# Example "config_files" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

import configparser
import tomllib

ini = """
[DEFAULT]
debug = no

[server]
host = example.com
port = 8080

[paths]
base = /srv/app
logs = %(base)s/logs
"""
config = configparser.ConfigParser()
config.read_string(ini)
print(config.sections())
print(config["server"]["host"], config.getint("server", "port"), config.getboolean("server", "debug"))
print(config.get("paths", "logs"))                    # %(base)s is filled in
print(config.get("server", "timeout", fallback="30"))

toml = """
title = "Shop"

[database]
ports = [5432, 5433]
enabled = true
"""
data = tomllib.loads(toml)
print(data["title"], data["database"]["ports"], type(data["database"]["enabled"]).__name__)
