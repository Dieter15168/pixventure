from main.models import Setting
from media.config import DEFAULT_MEDIA_SETTINGS

class MediaSettingsProvider:
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
            return DEFAULT_MEDIA_SETTINGS.get(key)

    @staticmethod
    def get_all_settings():
        """
        Returns a dictionary of all media settings.
        """
        settings = {}
        for key, default in DEFAULT_MEDIA_SETTINGS.items():
            settings[key] = MediaSettingsProvider.get_setting(key)
        return settings
