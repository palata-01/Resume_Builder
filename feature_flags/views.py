from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FeatureToggle

@api_view(['GET'])
def get_features(request):
    feature_settings = FeatureToggle.get_settings()
    return Response({
        "download_enabled": feature_settings.download_enabled,
        "print_enabled": feature_settings.print_enabled,
        "email_enabled": feature_settings.email_enabled,
        "whatsapp_enabled": feature_settings.whatsapp_enabled,
        "password_protection_enabled": feature_settings.password_protection_enabled,
    })