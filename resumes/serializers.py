from rest_framework import serializers
from .models import Resume
import phonenumbers

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = [
            'resume_id',
            'word_count',
            'character_count',
            'paragraph_count',
            'reading_time',
            'pdf_file',
            'pdf_password',
            'download_count',
            'download_expires_at',
            'created_at',
            'updated_at',
        ]

    def validate_phone(self, value):
        try:
            parsed = phonenumbers.parse(value, "IN")
            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Invalid phone number.")
        except Exception:
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate(self, attrs):
        required_fields = ['full_name', 'email', 'phone', 'dob']
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError({field: f"{field} is required."})

        summary = attrs.get('summary', '')
        skills = attrs.get('skills', [])
        all_text = summary + " " + " ".join(skills)
        word_count = len(all_text.split())

        if word_count > 1200:
            raise serializers.ValidationError("Resume content is too large.")

        return attrs