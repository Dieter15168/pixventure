from main.models import Setting
from main.default_settings_config import DEFAULT_SETTINGS

class SettingsProvider:
    """
    Fetches media settings from the main app's Setting model if available,
    otherwise returns default configuration values.
    """

    @staticmethod
    def get_setting(key: str):
        """
        Get a single setting value by key.
        """
        try:
            setting = Setting.objects.get(key=key)
            return setting.value
        except Setting.DoesNotExist:
            return DEFAULT_SETTINGS.get(key)

    @staticmethod
    def get_all_settings():
        """
        Returns a dictionary of all media settings.
        """
        settings = {}
        for key, default in DEFAULT_SETTINGS.items():
            settings[key] = SettingsProvider.get_setting(key)
        return settings
