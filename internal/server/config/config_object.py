import os
import yaml
import re
from internal.server.config.config_object import Config, App, Database, Api, Test

# Path to config.yaml
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../config/config.yaml'))

# Pattern for ${ENV_VAR:-default}
ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

def resolve_env_var(value: str) -> str:
    def replacer(match):
        expr = match.group(1)
        if ':-' in expr:
            var, default = expr.split(':-', 1)
            return os.environ.get(var, default)
        return os.environ.get(expr, '')
    return ENV_VAR_PATTERN.sub(replacer, value)

def env_var_constructor(loader, node):
    raw_value = loader.construct_scalar(node)
    return resolve_env_var(raw_value)

class EnvVarLoader(yaml.SafeLoader):
    pass

EnvVarLoader.add_constructor('tag:yaml.org,2002:str', env_var_constructor)
EnvVarLoader.add_implicit_resolver('!env_var', ENV_VAR_PATTERN, ['$'])

# Load and parse the config file
with open(CONFIG_PATH, 'r') as f:
    raw_config = yaml.load(f, Loader=EnvVarLoader)

CONFIG = Config(
    app=App(**raw_config.get('app', {})),
    database=Database(**raw_config.get('database', {})),
    api=Api(**raw_config.get('api', {})),
    test=Test(**raw_config.get('test', {})),
)
