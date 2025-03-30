from django.shortcuts import render
from rest_framework import viewsets

from .models import Course, Lecturer
from .serializers import CourseSerializer, LecturerSerializer

# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer