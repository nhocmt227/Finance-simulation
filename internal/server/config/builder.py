from typing import Dict
from internal.server.config.config_object import (
    Config,
    App,
    Database,
    Core,
    Logger,
    Bugger,
    Api,
    Test,
)


def build_config_from_dict(raw: Dict) -> Config:
    print("------------------------ CONFIG INITIALIZE ------------------------")
    return Config(
        app=App(**raw.get("app", {})),
        database=Database(**raw.get("database", {})),
        core=Core(
            logger=Logger(**raw.get("core", {}).get("logger", {})),
            bugger=Bugger(**raw.get("core", {}).get("bugger", {})),
        ),
        api=Api(**raw.get("api", {})),
        test=Test(**raw.get("test", {})),
    )
