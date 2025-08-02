# === Top-level Configuration Structure ===
class Config:
    def __init__(self, app, database, core, api, payment, test):
        self.app = app
        self.database = database
        self.core = core
        self.api = api
        self.payment = payment
        self.test = test


# === Individual Configuration Sections ===


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


class Core:
    def __init__(self, logger, bugger):
        self.logger = logger
        self.bugger = bugger


class Logger:
    def __init__(self, level, filename):
        self.level = level
        self.filename = filename


class Bugger:
    def __init__(self, filename):
        self.filename = filename


class Api:
    def __init__(self, time_to_update_second):
        self.time_to_update_second = time_to_update_second


class Payment:
    def __init__(self, platform_fee):
        self.platform_fee = platform_fee


class Test:
    def __init__(self, mock_boolean, mock_string, mock_integer, mock_float):
        self.mock_boolean = mock_boolean
        self.mock_string = mock_string
        self.mock_integer = mock_integer
        self.mock_float = mock_float
