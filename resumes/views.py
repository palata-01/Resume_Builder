from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, render
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer
from .utils import calculate_resume_stats, generate_pdf, protect_pdf
from logs.models import ActivityLog
from feature_flags.models import FeatureToggle

# def is_submission_open():
#     deployed_at = timezone.make_aware(settings.APP_DEPLOYED_AT)
#     return timezone.now() <= deployed_at + timedelta(minutes=settings.FORM_ACCESS_MINUTES)
def is_submission_open():
    return True

@api_view(['GET', 'POST'])
def resume_list_create(request):
    if request.method == 'GET':
        resumes = Resume.objects.all().order_by('-created_at')
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not is_submission_open():
            return Response(
                {"error": "Resume submission time has expired."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            resume = serializer.save()

            words, chars, paragraphs, reading_time = calculate_resume_stats(resume)
            resume.word_count = words
            resume.character_count = chars
            resume.paragraph_count = paragraphs
            resume.reading_time = reading_time
            resume.save()

            ActivityLog.objects.create(resume=resume, action='created')
            return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk)

    if request.method == 'GET':
        return Response(ResumeSerializer(resume).data)

    if request.method == 'PUT':
        serializer = ResumeSerializer(resume, data=request.data)
        if serializer.is_valid():
            resume = serializer.save()

            words, chars, paragraphs, reading_time = calculate_resume_stats(resume)
            resume.word_count = words
            resume.character_count = chars
            resume.paragraph_count = paragraphs
            resume.reading_time = reading_time
            resume.save()

            ActivityLog.objects.create(resume=resume, action='updated')
            return Response(ResumeSerializer(resume).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        resume.delete()
        return Response({"message": "Resume deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
@api_view(["POST"])
def generate_resume_pdf(request, pk):
    resume = get_object_or_404(Resume, pk=pk)

    try:
        feature_settings = FeatureToggle.get_settings()
        password_enabled = feature_settings.password_protection_enabled
    except Exception:
        password_enabled = True

    try:
        pdf_buffer = generate_pdf(resume)
    except Exception as e:
        return Response(
            {"error": f"PDF generation failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    password = f"{resume.full_name.replace(' ', '')}-{resume.dob.strftime('%d%m%Y')}"

    try:
        if password_enabled:
            pdf_buffer = protect_pdf(pdf_buffer, password)
            resume.pdf_password = password
        else:
            resume.pdf_password = ""

        filename = f"{resume.resume_id}.pdf"
        resume.pdf_file.save(filename, ContentFile(pdf_buffer.read()), save=False)
        resume.download_expires_at = timezone.now() + timedelta(hours=24)
        resume.save()

        try:
            ActivityLog.objects.create(resume=resume, action="pdf_generated")
        except Exception:
            pass

        return Response({
            "message": "PDF generated successfully",
            "resume_id": resume.resume_id,
            "pdf_url": request.build_absolute_uri(resume.pdf_file.url) if resume.pdf_file else None,
            "password": resume.pdf_password if password_enabled else None,
            "expires_at": resume.download_expires_at,
            "saved_file_name": resume.pdf_file.name if resume.pdf_file else None
        })

    except Exception as e:
        return Response(
            {"error": f"Error while saving PDF: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def download_resume(request, pk):
    resume = get_object_or_404(Resume, pk=pk)

    if not resume.pdf_file:
        return Response({"error": "PDF not generated yet."}, status=status.HTTP_400_BAD_REQUEST)

    if resume.is_download_expired():
        return Response(
            {"error": "This resume link has expired. Please generate again."},
            status=status.HTTP_400_BAD_REQUEST
        )

    resume.download_count += 1
    resume.save(update_fields=["download_count"])

    try:
        ActivityLog.objects.create(resume=resume, action="downloaded")
    except Exception:
        pass

    return Response({
        "pdf_url": request.build_absolute_uri(resume.pdf_file.url),
        "download_count": resume.download_count,
        "file_name": resume.pdf_file.name
    })
from django.shortcuts import render

def resume_builder_page(request):
    return render(request, 'resumes/index.html')
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer

def resume_builder_page(request):
    return render(request, 'resumes/index.html')

def is_submission_open():
    return True

@api_view(['GET', 'POST'])
def resume_list_create(request):
    if request.method == 'GET':
        resumes = Resume.objects.all().order_by('-created_at')
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)

    serializer = ResumeSerializer(data=request.data)
    if serializer.is_valid():
        resume = serializer.save()
        return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def resume_detail(request, pk):
    resume = get_object_or_404(Resume, pk=pk)

    if request.method == 'GET':
        return Response(ResumeSerializer(resume).data)

    if request.method == 'PUT':
        serializer = ResumeSerializer(resume, data=request.data)
        if serializer.is_valid():
            resume = serializer.save()
            return Response(ResumeSerializer(resume).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    resume.delete()
    return Response({"message": "Resume deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
