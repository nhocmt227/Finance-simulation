import os
import yaml
import re

class Config:
    def __init__(self, app, database, api, test):
        self.app = app
        self.database = database
        self.api = api
        self.test = test

class App:
    def __init__(self, host, port, url, debug):
        self.host = host
        self.port = port
        self.url = url
        self.debug = debug

class Database:
    def __init__(self, db_name, db_type, timeout_second):
        self.db_name = db_name
        self.db_type = db_type
        self.timeout_second = timeout_second

class Api:
    def __init__(self, time_to_update_second):
        self.time_to_update_second = time_to_update_second

class Test:
    def __init__(self, mock_boolean, mock_string, mock_integer, mock_float):
        self.mock_boolean = mock_boolean
        self.mock_string = mock_string
        self.mock_integer = mock_integer
        self.mock_float = mock_float

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config/config.yaml'))
ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

# --- Function to resolve environment variable expressions ---
def resolve_env_var(value: str) -> str:
    def replacer(match):
        expr = match.group(1)
        if ':-' in expr:
            var, default = expr.split(':-', 1)
            return os.environ.get(var, default)
        return os.environ.get(expr, '')
    return ENV_VAR_PATTERN.sub(replacer, value)

# --- Custom YAML constructor for environment-interpolated strings ---
def env_var_constructor(loader, node):
    raw_value = loader.construct_scalar(node)
    return resolve_env_var(raw_value)

# --- Custom SafeLoader that injects env var interpolation ---
class EnvVarLoader(yaml.SafeLoader):
    pass

# Register the constructor for both explicit and implicit environment var usage
EnvVarLoader.add_constructor('tag:yaml.org,2002:str', env_var_constructor)
EnvVarLoader.add_implicit_resolver('!env_var', ENV_VAR_PATTERN, ['$'])

with open(CONFIG_PATH, 'r') as f:
    raw_config = yaml.load(f, Loader=EnvVarLoader)

CONFIG = Config(
    app=App(**raw_config.get('app', {})),
    database=Database(**raw_config.get('database', {})),
    api=Api(**raw_config.get('api', {})),
    test=Test(**raw_config.get('test', {})),
)