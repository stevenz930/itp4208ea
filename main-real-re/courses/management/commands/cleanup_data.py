from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import (
    Subject, CourseCategory, Course, Tag, Lesson, 
    Enrollments, Review, LessonProgress
)
from django.db import connection
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Completely removes all test data and resets SQLite IDs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("\n=== Starting Database Cleanup ==="))
        
        User = get_user_model()
        self.clean_database(User)
        self.clean_media_files()
        self.reset_sequences()
        
        self.stdout.write(self.style.SUCCESS("\n✔ Database fully reset!\n"))

    def clean_database(self, User):
        """Delete all data in correct dependency order"""
        self.stdout.write("\n1. Cleaning database records...")
        
        # Order matters - most dependent models first
        models_to_clear = [
            LessonProgress,  # Depends on Enrollments and Lesson
            Review,         # Depends on Course and User
            Enrollments,    # Depends on Course and User
            Lesson,         # Depends on Course
            Course,         # Depends on Category and User
            CourseCategory, # Depends on Subject
            Tag,           # Independent
            Subject        # Independent
        ]

        for model in models_to_clear:
            try:
                count = model.objects.count()
                model.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f"  ✔ Deleted {count} {model.__name__} records")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ⚠ Error deleting {model.__name__}: {str(e)}")
                )

        # Clean users with different patterns
        try:
            user_patterns = [
                "email__endswith='@school.edu'",
                "username__startswith='prof_'",
                "username__startswith='student_'",
                "username__startswith='instructor_'"
            ]
            
            total_deleted = 0
            for pattern in user_patterns:
                deleted_count = User.objects.filter(**{pattern.split('=')[0]: pattern.split('=')[1].strip("'")}).count()
                User.objects.filter(**{pattern.split('=')[0]: pattern.split('=')[1].strip("'")}).delete()
                total_deleted += deleted_count
                
            self.stdout.write(
                self.style.SUCCESS(f"  ✔ Deleted {total_deleted} test users")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ⚠ Error deleting users: {str(e)}")
            )

    def clean_media_files(self):
        """Clean all media directories"""
        self.stdout.write("\n2. Cleaning media files...")
        
        media_dirs = {
            'Avatars': os.path.join(settings.MEDIA_ROOT, 'avatars'),
            'Course Thumbnails': os.path.join(settings.MEDIA_ROOT, 'course_thumbnails'),
            'Course Materials': os.path.join(settings.MEDIA_ROOT, 'course_materials')
        }

        for dir_name, dir_path in media_dirs.items():
            try:
                if os.path.exists(dir_path):
                    # Count files before deletion
                    file_count = sum(len(files) for _, _, files in os.walk(dir_path))
                    
                    # Remove directory and recreate it
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path, exist_ok=True)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✔ Cleaned {dir_name}: {file_count} files removed")
                    )
                else:
                    os.makedirs(dir_path, exist_ok=True)
                    self.stdout.write(
                        self.style.NOTICE(f"  ℹ Created new {dir_name} directory")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ⚠ Error cleaning {dir_name}: {str(e)}")
                )

    def reset_sequences(self):
        """Reset all SQLite auto-increment counters"""
        self.stdout.write("\n3. Resetting database sequences...")
        
        tables = [
            'courses_lessonprogress',
            'courses_review',
            'courses_enrollments',
            'courses_lesson',
            'courses_course',
            'courses_coursecategory',
            'courses_subject',
            'courses_tag',
            'users_customuser'
        ]

        with connection.cursor() as cursor:
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✔ Reset sequence for {table}")
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ⚠ Error resetting {table}: {str(e)}")
                    )