# Developer Guide
Feel free to update this guide as you update the code.

## Helper package:
### logger
- Used for logging purpose. The log location can be found in the `config.yaml` file.
- Can support multi-level logging, for example: `DEBUG, INFO, WARNING, ERROR, CRITICAL`.
### bugger
- Used for bug reporting purpose, for example: UserID not found.
- The log location can be found in the `config.yaml` file.

## How to create and update config values:
### Edit `config.yaml`
- Add your config under a section (or new one). Use `${ENV_VAR:-default}` if needed.
### Update `config.py` and `config_object.py`
- Add a class for the new config section (if needed).