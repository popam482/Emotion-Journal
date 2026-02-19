import json
import os

class SettingsManager:
    def __init__(self, file_path="settings.json"):
        self.file_path = file_path
        self.defaults = {
            "theme_mode": "dark",
            "scan_duration": 10
        }
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return {**self.defaults, **json.load(f)}
            except:
                return self.defaults
        return self.defaults

    def save_settings(self):
        with open(self.file_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()