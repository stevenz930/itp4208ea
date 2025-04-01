from django.shortcuts import render
from rest_framework import viewsets, filters

from .models import Course, Lecturer
from .serializers import CourseSerializer, CourseTypeSerializer, LecturerSerializer


# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):#all data in Course
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
class CourseTypeViewSet(viewsets.ModelViewSet):#get courseType in Course & distinct
    serializer_class = CourseTypeSerializer

    def get_queryset(self):
        return Course.objects.values('courseType').distinct()

class CourseFiltByTypeViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['courseType']

class LecturerViewSet(viewsets.ModelViewSet):#all data in Lecturer
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
