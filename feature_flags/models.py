from django.db import models

class FeatureToggle(models.Model):
    download_enabled = models.BooleanField(default=True)
    print_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=True)
    password_protection_enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Feature Toggles"