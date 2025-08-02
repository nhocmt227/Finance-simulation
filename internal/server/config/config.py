from typing import Dict
from internal.server.config.config_object import (
    Config,
    App,
    Database,
    Core,
    Logger,
    Bugger,
    Api,
    Payment,
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
        payment=Payment(**raw.get("payment", {})),
        test=Test(**raw.get("test", {})),
    )
