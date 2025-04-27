import os

class ConfigReader:
    @staticmethod
    def get_value(key, default=None):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config.txt")
        config_path = os.path.abspath(config_path)

        if not os.path.isfile(config_path):
            print(f"Config file not found at {config_path}. Using default value.")
            return default

        with open(config_path, "r") as file:
            for line in file:
                if line.strip().startswith(f"{key}="):
                    return line.strip().split("=", 1)[1]
        print(f"Key '{key}' not found in config file. Using default value.")
        return default