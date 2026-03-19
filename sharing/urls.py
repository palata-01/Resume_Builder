from django.urls import path
from .views import share_email, share_whatsapp

urlpatterns = [
    path("<int:pk>/email/", share_email, name="share_email"),
    path("<int:pk>/whatsapp/", share_whatsapp, name="share_whatsapp"),
]