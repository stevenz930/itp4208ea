# courses/management/commands/generate_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Subject, CourseCategory, Course, Tag, Lesson, Enrollments
import random
from datetime import timedelta
from django.utils.text import slugify
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Generates complete test data with subjects, categories, courses and enrollments'

    def handle(self, *args, **options):
        User = get_user_model()
        
        print("\n=== Starting Test Data Generation ===")

        # 1. First delete any existing test data
        self.clean_test_data(User)

        # 2. Create Subjects
        subjects = self.create_subjects()
        
        # 3. Create Instructors
        instructors = self.create_instructors(User)
        
        # 4. Create Subcategories
        subcategories = self.create_subcategories(subjects)
        
        # 5. Create Tags (AFTER instructors exist)
        tags = self.create_tags(instructors)
        
        # 6. Create Courses
        courses = self.create_courses(subcategories, instructors, tags)
        
        # 7. Create Students and Enrollments
        self.create_students_and_enrollments(User, courses)

        print("\n=== Test Data Generation Complete ===")
        print(f"Total Courses Created: {Course.objects.count()}")
        print(f"Total Lessons Created: {Lesson.objects.count()}")
        print(f"Total Enrollments: {Enrollments.objects.count()}\n")

    def clean_test_data(self, User):
        """Delete any existing test data"""
        Lesson.objects.all().delete()
        Enrollments.objects.all().delete()
        Course.objects.all().delete()
        CourseCategory.objects.all().delete()
        Subject.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.filter(username__startswith='instructor_').delete()
        User.objects.filter(username__startswith='student_').delete()
        print("Cleaned existing test data")

    def create_subjects(self):
        """Create 3 main subjects"""
        subjects_data = [
            {"name": "Data Science", "slug": "data-science"},
            {"name": "Web Development", "slug": "web-development"},
            {"name": "Artificial Intelligence", "slug": "artificial-intelligence"}
        ]
        
        subjects = []
        for data in subjects_data:
            try:
                subject = Subject.objects.create(
                    name=data["name"],
                    slug=data["slug"],
                    is_active=True
                )
            except IntegrityError:
                subject = Subject.objects.create(
                    name=data["name"],
                    slug=f"{data['slug']}-{random.randint(1000,9999)}",
                    is_active=True
                )
            subjects.append(subject)
        print(f"Created {len(subjects)} subjects")
        return subjects

    def create_instructors(self, User):
        """Create 15 instructors using your CustomUser model"""
        instructors = []
        for i in range(1, 16):
            instructor = User.objects.create_user(
                email=f"instructor{i}@example.com",
                username=f"instructor_{i}",
                password='testpass123',
                is_instructor=True,
                profile_public=True
            )
            instructors.append(instructor)
        print(f"Created {len(instructors)} instructors")
        return instructors

    def create_subcategories(self, subjects):
        """Create 3 subcategories per subject"""
        subcategories = []
        subcategory_data = {
            "Data Science": ["Fundamentals", "Machine Learning", "Data Visualization"],
            "Web Development": ["Frontend", "Backend", "Full Stack"],
            "Artificial Intelligence": ["Computer Vision", "NLP", "Generative AI"]
        }

        for subject in subjects:
            for subcat_name in subcategory_data[subject.name]:
                subcategory = CourseCategory.objects.create(
                    subject=subject,
                    name=f"{subject.name} - {subcat_name}",
                    slug=slugify(f"{subject.slug}-{subcat_name}")
                )
                subcategories.append(subcategory)
        print(f"Created {len(subcategories)} subcategories")
        return subcategories

    def create_tags(self, instructors):
        """Create 5 common tags"""
        tags = [
            Tag.objects.create(name="Beginner", Created_by=random.choice(instructors)),
            Tag.objects.create(name="Intermediate", Created_by=random.choice(instructors)),
            Tag.objects.create(name="Advanced", Created_by=random.choice(instructors)),
            Tag.objects.create(name="Project-Based", Created_by=random.choice(instructors)),
            Tag.objects.create(name="Certification", Created_by=random.choice(instructors))
        ]
        print(f"Created {len(tags)} tags")
        return tags

    def create_courses(self, subcategories, instructors, tags):
        """Create 10 courses per subcategory"""
        course_titles = {
            "Data Science": [
                "Python for Data Analysis", "Pandas Masterclass", "Data Cleaning Techniques",
                "SQL for Data Science", "Statistical Modeling", "Time Series Analysis",
                "Big Data Fundamentals", "Data Storytelling", "Experimental Design",
                "Business Analytics"
            ],
            "Web Development": [
                "HTML/CSS Fundamentals", "JavaScript Deep Dive", "React.js Complete Guide",
                "Node.js Backend Development", "Django Web Framework", "REST API Design",
                "Web Security Essentials", "Responsive Design", "Web Performance Optimization",
                "Progressive Web Apps"
            ],
            "Artificial Intelligence": [
                "Neural Networks 101", "TensorFlow for Beginners", "Computer Vision Basics",
                "Natural Language Processing", "Generative Adversarial Networks",
                "Reinforcement Learning", "AI Ethics", "Model Deployment",
                "Transfer Learning", "AI for Healthcare"
            ]
        }

        courses = []
        for subcategory in subcategories:
            subject_name = subcategory.subject.name
            for i in range(10):  # 10 courses per subcategory
                title = course_titles[subject_name][i]
                course = Course.objects.create(
                    title=title,
                    description=f"Comprehensive course on {title}. Learn all the essential concepts.",
                    category=subcategory,
                    instructor=random.choice(instructors),
                    price=random.choice([19.99, 29.99, 39.99, 49.99, 59.99]),
                    level=random.choice(['BG', 'IM', 'AD']),
                    thumbnail='course_thumbnails/placeholder.jpg',
                    is_published=True,
                    applications_covered="Various tools and technologies"
                )
                course.tags.set(random.sample(tags, 2))
                
                # Create 5 lessons per course
                for lesson_num in range(1, 6):
                    Lesson.objects.create(
                        course=course,
                        title=f"Lesson {lesson_num}: {title.split()[0]} Basics",
                        order=lesson_num,
                        content=f"This lesson covers {title.split()[0]} fundamentals.",
                        is_free=(lesson_num == 1),
                        duration=timedelta(minutes=random.randint(15, 45)),
                        video_url=f"https://example.com/videos/{slugify(title)}-{lesson_num}"
                    )
                
                courses.append(course)
        print(f"Created {len(courses)} courses with lessons")
        return courses

    def create_students_and_enrollments(self, User, courses):
        """Create 50 students with enrollments"""
        students = []
        for i in range(1, 51):
            student = User.objects.create_user(
                email=f"student{i}@example.com",
                username=f"student_{i}",
                password='testpass123',
                is_instructor=False,
                profile_public=True
            )
            students.append(student)
            
            # Enroll each student in 3 random courses
            for course in random.sample(courses, 3):
                Enrollments.objects.create(
                    student=student,
                    Course=course
                )
        print(f"Created {len(students)} students with enrollments")