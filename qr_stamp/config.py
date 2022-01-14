import json
import os
from pathlib import Path
import sys

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    CONFIG_FILE = Path("configs.json")
else:
    CONFIG_FILE = dir_path / "configs.json"

parameters = dict()

with open(CONFIG_FILE, 'r') as config_file:
    json_configs = config_file.read()
    parameters = json.loads(json_configs)


def save():
    with open(CONFIG_FILE, 'w') as config_file:
        config_file.write(json.dumps(parameters))
