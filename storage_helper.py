import json
from gpio_utils import GPIO_MAP, check_pinout  # Import the GPIO utilities

class Storage_Helper:
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
        try:
            with open(self.settings_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Handle missing or corrupted JSON gracefully
            return {}

    def read_from_file(self, file_path, key=None):
        """
        Read data from a JSON file. If a key is provided, return its value.
        :param file_path: The path to the file to read.
        :param key: The key to look up in the JSON file. If None, return all data.
        :return: The value associated with the key, or all data if no key is provided.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                return data.get(key) if key else data
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def write_to_file(self, file_path, key, value):
        """
        Write a key-value pair to a JSON file. Creates the file if it doesn't exist.
        :param file_path: The path to the file to write.
        :param key: The key to update in the file.
        :param value: The value to associate with the key.
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}  # Start fresh if the file is missing or corrupted

        # Update the key-value pair
        data[key] = value

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def reset_to_defaults(self):
        """
        Overwrite the settings file with the contents of the default file.
        """
        try:
            with open(self.default_file, "r") as f:
                default_data = json.load(f)
            with open(self.settings_file, "w") as f:
                json.dump(default_data, f, indent=4)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Default file '{self.default_file}' is missing!") from e

    def read_from_settings(self, key=None):
        """
        Read data from the settings file (cache). Supports nested keys.
        :param key: The key to look up, supports nested keys separated by a dot (e.g., "clutch.bits").
        :return: The value associated with the key, or all data if no key is provided.
        """
        if not key:
            return self._cache

        keys = key.split(".")
        current = self._cache

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None  # Key not found

        return current

    def write_to_settings(self, key, value):
        """
        Write a value to a specific key or nested key in the settings file and update the cache.
        :param key: The key to update, supports nested keys separated by a dot (e.g., "clutch.bits").
        :param value: The value to associate with the key.
        """
        keys = key.split(".")
        current = self._cache

        # Traverse to the correct dictionary level
        for k in keys[:-1]:
            current = current.setdefault(k, {})

        # Update the value at the final key
        current[keys[-1]] = value

        # Write the updated settings back to the file
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self._cache, f, indent=4)
        except OSError as e:
            print(f"Error writing settings file: {e}")

    def read_from_defaults(self, key=None):
        """
        Read data from the default file. If a key is provided, return its value.
        :param key: The key to look up in the default file. If None, return all data.
        :return: The value associated with the key, or all data if no key is provided.
        """
        return self.read_from_file(self.default_file, key)

    def validate_pinout(self):
        """
        Validate the pinout configuration using the GPIO map.
        """
        settings = self.read_from_settings()
        if not settings:
            print("Error: No settings found. Unable to validate pinout.")
            return

        check_pinout(settings)
