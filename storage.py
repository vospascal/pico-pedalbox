import json
import os

class Storage:
    def __init__(self, settings_file="settings.json", default_file="default.json"):
        """
        Initialize the Storage class with file paths for settings and defaults.
        Cache the contents of settings.json for quick access.
        """
        self.settings_file = settings_file
        self.default_file = default_file
        self._cache = self._load_cache()

    def _load_cache(self):
        """
        Load the contents of the settings file into the cache.
        :return: A dictionary containing the settings data.
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted JSON gracefully
                return {}
        return {}

    def read_from_file(self, file_path, key=None):
        """
        Read data from a JSON file. If a key is provided, return its value.
        :param file_path: The path to the file to read.
        :param key: The key to look up in the JSON file. If None, return all data.
        :return: The value associated with the key, or all data if no key is provided.
        """
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get(key) if key else data
        except json.JSONDecodeError:
            # Handle corrupted JSON gracefully
            return None

    def write_to_file(self, file_path, key, value):
        """
        Write a key-value pair to a JSON file. Creates the file if it doesn't exist.
        :param file_path: The path to the file to write.
        :param key: The key to update in the file.
        :param value: The value to associate with the key.
        """
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted JSON by starting fresh
                data = {}

        # Update the key-value pair
        data[key] = value

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def reset_to_defaults(self):
        """
        Overwrite the settings file with the contents of the default file.
        """
        if not os.path.exists(self.default_file):
            raise FileNotFoundError(f"Default file '{self.default_file}' is missing!")

        with open(self.default_file, "r") as f:
            default_data = json.load(f)

        with open(self.settings_file, "w") as f:
            json.dump(default_data, f, indent=4)

    def read_from_settings(self, key=None):
        """
        Read data from the settings file (cache) or from the file itself if key is not cached.
        :param key: The key to look up in the settings file. If None, return all data.
        :return: The value associated with the key, or all data if no key is provided.
        """
        return self._cache.get(key) if key else self._cache

    def write_to_settings(self, key, value):
        """
        Write a key-value pair to the settings file and update the cache.
        :param key: The key to update in the settings file.
        :param value: The value to associate with the key.
        """
        self._cache[key] = value  # Update the cache
        self.write_to_file(self.settings_file, key, value)

    def read_from_defaults(self, key=None):
        """
        Read data from the default file. If a key is provided, return its value.
        :param key: The key to look up in the default file. If None, return all data.
        :return: The value associated with the key, or all data if no key is provided.
        """
        return self.read_from_file(self.default_file, key)
