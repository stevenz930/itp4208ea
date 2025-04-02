#!/usr/bin/env python
import os
import random
from datetime import timedelta

def generate_test_data():
    # 1. Setup Django Environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
    import django
    django.setup()
    
    # 2. Now import your models AFTER Django is setup
    from django.contrib.auth import get_user_model
    from courses.models import Subject, CourseCategory, Course, Tag, Lesson, Enrollments

    User = get_user_model()
    
    print("\n=== Starting Test Data Generation ===")

    # 1. Create Subjects
    subjects = [
        Subject.objects.create(
            name="Data Science",
            slug="data-science",
            is_active=True
        ),
        Subject.objects.create(
            name="Web Development",
            slug="web-development",
            is_active=True
        ),
        Subject.objects.create(
            name="Artificial Intelligence",
            slug="artificial-intelligence",
            is_active=True
        )
    ]
    print(f"Created {len(subjects)} subjects")

    # 2. Create Instructors (15 total - 5 per subject)
    instructors = []
    for i in range(1, 16):
        instructor = User.objects.create_user(
            username=f"instructor_{i}",
            email=f"instructor{i}@example.com",
            password='testpass123',
            is_instructor=True
        )
        instructors.append(instructor)
    print(f"Created {len(instructors)} instructors")

    # 3. Create Subcategories (3 per subject)
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
                slug=f"{subject.slug}-{subcat_name.lower().replace(' ', '-')}"
            )
            subcategories.append(subcategory)
    print(f"Created {len(subcategories)} subcategories")

    # 4. Create Tags
    tags = [
        Tag.objects.create(name="Beginner", Created_by=random.choice(instructors)),
        Tag.objects.create(name="Intermediate", Created_by=random.choice(instructors)),
        Tag.objects.create(name="Advanced", Created_by=random.choice(instructors)),
        Tag.objects.create(name="Project-Based", Created_by=random.choice(instructors)),
        Tag.objects.create(name="Certification", Created_by=random.choice(instructors))
    ]
    print(f"Created {len(tags)} tags")

    # 5. Create Courses (10 per subcategory)
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
                description=f"Comprehensive course on {title}. Learn all the essential concepts and practical applications.",
                category=subcategory,
                instructor=instructors.pop(0),  # Assign different instructor to each course
                price=random.choice([19.99, 29.99, 39.99, 49.99, 59.99]),
                level=random.choice(['BG', 'IM', 'AD']),
                thumbnail='course_thumbnails/placeholder.jpg',
                is_published=True
            )
            course.tags.set(random.sample(tags, 2))  # Assign 2 random tags
            courses.append(course)
            
            # Create 5 lessons for each course
            for lesson_num in range(1, 6):
                Lesson.objects.create(
                    course=course,
                    title=f"Lesson {lesson_num}: {title.split()[0]} Basics",
                    order=lesson_num,
                    content=f"This lesson covers the fundamental concepts of {title.split()[0]}.",
                    is_free=(lesson_num == 1),  # First lesson free
                    duration=timedelta(minutes=random.randint(15, 45))
                )
    print(f"Created {len(courses)} courses with lessons")

    # 6. Create Students and Enrollments
    students = []
    for i in range(1, 51):  # 50 students
        student = User.objects.create_user(
            username=f"student_{i}",
            email=f"student{i}@example.com",
            password='testpass123',
            is_instructor=False
        )
        students.append(student)
        
        # Enroll each student in 3 random courses
        for course in random.sample(courses, 3):
            Enrollments.objects.create(
                student=student,
                Course=course
            )
    print(f"Created {len(students)} students with enrollments")

    print("\n=== Test Data Generation Complete ===")
    print(f"Total Courses Created: {len(courses)}")
    print(f"Total Lessons Created: {Lesson.objects.count()}")
    print(f"Total Enrollments: {Enrollments.objects.count()}\n")

if __name__ == "__main__":
    generate_test_data()

# use to gen random data command>>
# python3 create_test_data.py

# clean data

# python3 manage.py shell -c "
# from django.contrib.auth import get_user_model;
# from courses.models import *;
# User = get_user_model();
# LessonProgress.objects.all().delete();
# Enrollments.objects.all().delete();
# Lesson.objects.all().delete();
# Course.objects.all().delete();
# CourseCategory.objects.all().delete();
# Subject.objects.all().delete();
# Tag.objects.all().delete();
# User.objects.filter(username__startswith='instructor_').delete();
# User.objects.filter(username__startswith='student_').delete();
# print('Deleted all test data');
# "