from typing import Dict, Any

class ConfigManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value

    def load_from_file(self, filepath: str):
        import json
        with open(filepath, 'r') as f:
            self.config = json.load(f)

    def save_to_file(self, filepath: str):
        import json
        with open(filepath, 'w') as f:
            json.dump(self.config, f, indent=4)
