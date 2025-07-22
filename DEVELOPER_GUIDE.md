# Developer Guide
Feel free to update this guide as you update the code.

## How to create and update config values:
### Edit `config.yaml`
- Add your config under a section (or new one). Use `${ENV_VAR:-default}` if needed.
### Update `config.py`
- Add a class for the new config section (if needed).
