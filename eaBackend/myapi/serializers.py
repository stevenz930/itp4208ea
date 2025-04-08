from rest_framework import serializers
from .models import Course, Lecturer

class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = ['id', 'name', 'description', 'avatar_url']

class CourseSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'price', 'description', 'lecturer', 'brief', 'pic_url', 'courseType']

    def create(self, validatedData):
        lecturerData = validatedData.pop('lecturer')#take lecturer data out
        lecturer, _ = Lecturer.objects.get_or_create(**lecturerData)#create or get lecturer object
        course = Course.objects.create(lecturer=lecturer, **validatedData)#create course object
        return course

class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['courseType']