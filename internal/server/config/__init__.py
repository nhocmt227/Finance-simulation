from internal.server.config.yaml_loader import load_raw_yaml_config
from internal.server.config.config import build_config_from_dict
from internal.server.config.config_object import Config

import os

CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../config/config.yaml")
)

raw_config = load_raw_yaml_config(CONFIG_PATH)
CONFIG: Config = build_config_from_dict(raw_config)
