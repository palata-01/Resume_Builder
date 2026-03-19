from django.db import models
from django.utils import timezone
from datetime import timedelta

class Resume(models.Model):
    resume_id = models.CharField(max_length=30, unique=True, blank=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    dob = models.DateField()

    title = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)

    skills = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    experience = models.JSONField(default=list, blank=True)
    projects = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)

    word_count = models.PositiveIntegerField(default=0)
    character_count = models.PositiveIntegerField(default=0)
    paragraph_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0)

    pdf_file = models.FileField(upload_to='resumes/', null=True, blank=True)
    pdf_password = models.CharField(max_length=255, blank=True)

    download_count = models.PositiveIntegerField(default=0)
    download_expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.resume_id:
            year = timezone.now().year
            count = Resume.objects.count() + 1001
            self.resume_id = f"RES-{year}-{count}"
        super().save(*args, **kwargs)

    def set_download_expiry(self):
        self.download_expires_at = timezone.now() + timedelta(hours=24)
        self.save(update_fields=['download_expires_at'])

    def is_download_expired(self):
        return self.download_expires_at and timezone.now() > self.download_expires_at

    def __str__(self):
        return self.resume_id