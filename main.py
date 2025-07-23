import sys
sys.path.insert(0, ".")
from cmd.server.server import app
from internal.server.config.config import CONFIG

if __name__ == "__main__":
    app.run(host=CONFIG.app.host, port=CONFIG.app.port, debug=CONFIG.app.debug)