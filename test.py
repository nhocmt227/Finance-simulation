from internal.server.config import CONFIG
from internal.core.logger import logger
from internal.core.bugger.bugger import bugger

# --- This file is extremely temporary ---
# --- TODO: Add proper integration test in place of this file ---


def test_config_values():
    print("==== Testing Config Values ====\n")

    print("[App Config]")
    print(f"Host: {CONFIG.app.host}")
    print(f"Port: {CONFIG.app.port}")
    print(f"URL: {CONFIG.app.url}")
    print(f"Debug: {CONFIG.app.debug}\n")

    print("[Database Config]")
    print(f"Name: {CONFIG.database.db_name}")
    print(f"Type: {CONFIG.database.db_type}")
    print(f"Timeout: {CONFIG.database.timeout_second}\n")

    print("[Core Config]")
    print(f"Logger Level: {CONFIG.core.logger.level}")
    print(f"Logger Filename: {CONFIG.core.logger.filename}\n")

    print("[API Config]")
    print(f"Time to update: {CONFIG.api.time_to_update_second}")


def test_logger():
    logger.info("This is an info message for testing.")
    logger.error("This is an error message for testing.")
    logger.warning("This is a warning message for testing.")
    logger.debug("This is a debug message for testing.")
    logger.critical("This is a critical message for testing.")


def test_bugger():
    bugger.log(
        {
            "error": "userID not found",
            "user_id": "12345",
            "action": "fetch_profile",
            "module": "UserService",
        }
    )


if __name__ == "__main__":
    test_config_values()
    test_logger()
    test_bugger()
