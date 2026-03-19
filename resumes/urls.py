from django.urls import path
from .views import (
    resume_list_create,
    resume_detail,
    generate_resume_pdf,
    download_resume,
)

urlpatterns = [
    path("", resume_list_create, name="resume_list_create"),
    path("<int:pk>/", resume_detail, name="resume_detail"),
    path("<int:pk>/generate-pdf/", generate_resume_pdf, name="generate_resume_pdf"),
    path("<int:pk>/download/", download_resume, name="download_resume"),
]