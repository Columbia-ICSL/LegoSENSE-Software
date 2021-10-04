# Configuration Utility for SensorHub Service
import os
import json

WEB_SERVER_PORT = 1515

if not os.path.exists('config.json'):
    with open('config.json', 'w') as f:
        default_module_cfg = dict(zip(['M1', 'M2', 'M3', 'M4'], [[] for i in range(4)]))
        json.dump(default_module_cfg, f)

with open('config.json', 'r') as f:
    INSTALLED_MODULES = json.load(f)
