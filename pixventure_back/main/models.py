# mainapp/models.py
from django.db import models

class Setting(models.Model):
    """
    A simple key-value store for application-wide settings.
    This allows dynamically updating settings without modifying code.
    """

    key = models.CharField(max_length=255, unique=True, help_text="Unique identifier for the setting.")
    value = models.CharField(max_length=1024, blank=True, help_text="Stored value for this setting.")

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = "Setting"
        verbose_name_plural = "Settings"
