from django.db import models
from resumes.models import Resume

class ShareHistory(models.Model):
    METHOD_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='shares')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    recipient = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.resume_id} - {self.method} - {self.recipient}"