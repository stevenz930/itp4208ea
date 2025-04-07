from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Subject, CourseCategory, Course, Tag, Lesson, Enrollments, Review
from django.db import connection
import os

class Command(BaseCommand):
    help = 'Completely removes all test data and resets SQLite IDs'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Delete all data
        models_to_clear = [
            Lesson, Enrollments, Course,
            CourseCategory, Subject, Tag, Review
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
            self.stdout.write(f"Deleted all {model.__name__} records")

        # Delete test users
        User.objects.filter(email__endswith="@school.edu").delete()
        User.objects.filter(username__startswith="prof_").delete()
        User.objects.filter(username__startswith="student_").delete()
        self.stdout.write("Deleted all test users")

        # Delete avatar images
        avatars_path = 'media/avatars'
        if os.path.exists(avatars_path):
            for filename in os.listdir(avatars_path):
                file_path = os.path.join(avatars_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.stdout.write(f"Deleted avatar: {filename}")
        else:
            self.stdout.write("No avatar directory found.")

        # Delete course thumbnails
        thumbnails_path = 'media/course_thumbnails'
        if os.path.exists(thumbnails_path):
            for filename in os.listdir(thumbnails_path):
                file_path = os.path.join(thumbnails_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.stdout.write(f"Deleted thumbnail: {filename}")
        else:
            self.stdout.write("No course thumbnails directory found.")

        # Reset SQLite auto-increment counters
        with connection.cursor() as cursor:
            tables = [
                'courses_subject', 'courses_coursecategory',
                'courses_course', 'courses_tag',
                'courses_lesson', 'courses_enrollments',
                'users_customuser', 'courses_review'
            ]
            for table in tables:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                self.stdout.write(f"Reset IDs for {table}")

        self.stdout.write(self.style.SUCCESS("✔ Database fully reset!"))