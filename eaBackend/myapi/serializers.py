from rest_framework import serializers
from .models import Course, Lecturer

class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()
    
    class Meta:
        model = Course
        fields = '__all__'