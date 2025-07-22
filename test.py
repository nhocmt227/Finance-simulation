from internal.server.config.config import CONFIG

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

    print("[API Config]")
    print(f"Time to update: {CONFIG.api.time_to_update_second}")

if __name__ == "__main__":
    test_config_values()
