from rest_framework import serializers
from .models import Subject, CourseCategory, Course, Lesson, Review

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'slug', 'is_active']

class CourseCategorySerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'slug', 'subject']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'order', 'duration']

class CourseSerializer(serializers.ModelSerializer):
    category = CourseCategorySerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category',
            'instructor', 'price', 'is_free', 'level',
            'thumbnail', 'average_rating', 'rating_count',
            'created_at', 'lessons'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'course', 'student', 'rating', 'comment', 'created_at']
        read_only_fields = ['student']
