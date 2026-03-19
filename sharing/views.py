from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMessage

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from resumes.models import Resume
from .models import ShareHistory
from logs.models import ActivityLog
from feature_flags.models import FeatureToggle


@api_view(["POST"])
def share_email(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    email = request.data.get("email", "").strip()

    if not email:
        return Response(
            {"error": "Email is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not resume.pdf_file:
        return Response(
            {"error": "Generate PDF first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        feature_settings = FeatureToggle.get_settings()
        if not feature_settings.email_enabled:
            return Response(
                {"error": "Email feature is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        pass

    if not settings.EMAIL_HOST_USER:
        return Response(
            {"error": "Sender email is not configured. Please set EMAIL_HOST_USER in .env"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        email_message = EmailMessage(
            subject=f"Resume - {resume.full_name}",
            body=f"Attached is the resume PDF.\n\nPassword: {resume.pdf_password}",
            from_email=settings.EMAIL_HOST_USER,
            to=[email],
        )

        email_message.attach_file(resume.pdf_file.path)
        email_message.send(fail_silently=False)

        try:
            ShareHistory.objects.create(
                resume=resume,
                method="email",
                recipient=email
            )
        except Exception:
            pass

        try:
            ActivityLog.objects.create(
                resume=resume,
                action="shared_email"
            )
        except Exception:
            pass

        return Response({
            "message": f"Resume shared via email successfully to {email}"
        })

    except Exception as e:
        return Response(
            {"error": f"Email sharing failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(["POST"])
def share_whatsapp(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    phone = request.data.get("phone", "").strip()

    if not phone:
        return Response(
            {"error": "Phone number is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    phone = "".join(ch for ch in phone if ch.isdigit())

    if not phone:
        return Response(
            {"error": "Invalid phone number."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not resume.pdf_file:
        return Response(
            {"error": "Generate PDF first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        feature_settings = FeatureToggle.get_settings()
        if not feature_settings.whatsapp_enabled:
            return Response(
                {"error": "WhatsApp feature is disabled."},
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        pass

    try:
        already_shared = ShareHistory.objects.filter(
            resume=resume,
            method="whatsapp",
            recipient=phone
        ).exists()

        if already_shared:
            return Response(
                {"error": "Resend option is disabled for this number."},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception:
        pass

    try:
        try:
            ShareHistory.objects.create(
                resume=resume,
                method="whatsapp",
                recipient=phone
            )
        except Exception:
            pass

        try:
            ActivityLog.objects.create(
                resume=resume,
                action="shared_whatsapp"
            )
        except Exception:
            pass

        pdf_url = request.build_absolute_uri(resume.pdf_file.url) if resume.pdf_file else ""

        whatsapp_text = (
            f"Hello, here is the resume of {resume.full_name}. "
            f"Password: {resume.pdf_password}. "
            f"Resume ID: {resume.resume_id}. "
            f"Download: {pdf_url}"
        )

        return Response({
            "message": "WhatsApp share prepared successfully.",
            "phone": phone,
            "whatsapp_text": whatsapp_text
        })

    except Exception as e:
        return Response(
            {"error": f"WhatsApp sharing failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )