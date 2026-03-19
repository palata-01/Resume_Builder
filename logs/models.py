from django.db import models
from resumes.models import Resume

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Resume created'),
        ('updated', 'Resume updated'),
        ('pdf_generated', 'PDF generated'),
        ('downloaded', 'Downloaded'),
        ('shared_email', 'Shared via Email'),
        ('shared_whatsapp', 'Shared via WhatsApp'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.resume_id} - {self.action}"