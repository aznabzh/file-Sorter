import json
import os


class ConfigHandler:
    def __init__(self, config_path):
        self.config_path = config_path
        self.folders = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        with open(self.config_path, 'r') as file:
            try:
                config = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in configuration file: {e}"
                )

        self.validate_config(config)
        return config.get("folders", [])

    def validate_config(self, config):
        if "folders" not in config:
            raise KeyError("Missing 'folders' key in configuration.")

        for folder in config["folders"]:
            if "directory" not in folder:
                raise KeyError("Missing 'directory' key in a folder.")
            if "rules" not in folder:
                raise KeyError("Missing 'rules' key in a folder.")
            for rule in folder["rules"]:
                if not isinstance(rule, dict):
                    raise ValueError("Each rule must be a dictionary.")
                if "destination" not in rule:
                    raise KeyError("Missing 'destination' key in a rule.")
                if (
                    "extensions" not in rule and
                    "filename_pattern" not in rule
                ):
                    raise ValueError(
                        "Each rule must have either 'extensions' or "
                        "'filename_pattern'."
                    )
                if (
                    "extensions" in rule and
                    not isinstance(rule["extensions"], list)
                ):
                    raise ValueError("'extensions' must be a list.")
                if (
                    "filename_pattern" in rule and
                    not isinstance(rule["filename_pattern"], str)
                ):
                    raise ValueError("'filename_pattern' must be a string.")