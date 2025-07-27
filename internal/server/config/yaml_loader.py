import os
import yaml
import re
from typing import Any, Dict

ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")


def resolve_env_var(value: str) -> str:
    def replacer(match):
        expr = match.group(1)
        if ":-" in expr:
            var, default = expr.split(":-", 1)
            return os.environ.get(var, default)
        return os.environ.get(expr, "")

    return ENV_VAR_PATTERN.sub(replacer, value)


class EnvVarLoader(yaml.SafeLoader):
    pass


def _add_env_var_support_to_yaml_loader():
    def env_var_constructor(loader, node):
        raw_value = loader.construct_scalar(node)
        return resolve_env_var(raw_value)

    EnvVarLoader.add_constructor("tag:yaml.org,2002:str", env_var_constructor)
    EnvVarLoader.add_implicit_resolver("!env_var", ENV_VAR_PATTERN, ["$"])


def load_raw_yaml_config(path: str) -> Dict[str, Any]:
    _add_env_var_support_to_yaml_loader()
    with open(path, "r") as file:
        return yaml.load(file, Loader=EnvVarLoader)
