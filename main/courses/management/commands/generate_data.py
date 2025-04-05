from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import Subject, CourseCategory, Course, Tag, Lesson, Enrollments,Review
import random
from datetime import timedelta
from django.utils.text import slugify
from django.db.utils import IntegrityError
from faker import Faker
import requests
from io import BytesIO
from django.core.files import File
from django.db import connection
import uuid
from PIL import Image, ImageDraw  # Requires Pillow: pip install pillow
import os

fake = Faker()

class Command(BaseCommand):
    help = 'Generates complete test data with IT-themed images and proper ID reset'

    def handle(self, *args, **options):
        User = get_user_model()
        
        print("\n=== Starting Data Generation ===")
        self.clean_test_data(User)
        
        subjects = self.create_subjects()
        instructors = self.create_instructors(User)
        subcategories = self.create_subcategories(subjects)
        tags = self.create_tags(instructors)
        courses = self.create_courses(subcategories, instructors, tags)
        self.create_students_and_enrollments(User, courses)

        print("\n=== Data Generation Complete ===")
        print(f"Subjects: {Subject.objects.count()}")
        print(f"Courses: {Course.objects.count()}")
        print(f"Users: {User.objects.count()}\n")

    def clean_test_data(self, User):
        """Delete all data and reset SQLite sequences"""
        models_to_clear = [
            Lesson, Enrollments, Course, 
            CourseCategory, Subject, Tag
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()

        User.objects.filter(username__startswith='instructor_').delete()
        User.objects.filter(username__startswith='student_').delete()

        # Reset SQLite auto-increment counters
        with connection.cursor() as cursor:
            tables = [
                'courses_subject', 'courses_coursecategory',
                'courses_course', 'courses_tag',
                'courses_lesson', 'courses_enrollments',
                'users_customuser'
            ]
            for table in tables:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        print("✔ Database cleaned and IDs reset")

    def create_subjects(self):
        subjects = [
            {"name": "Data Science", "slug": "data-science"},
            {"name": "Web Development", "slug": "web-dev"},
            {"name": "Artificial Intelligence", "slug": "ai"},
            {"name": "Cybersecurity", "slug": "cybersecurity"},
            {"name": "Mobile Development", "slug": "mobile-dev"},
            {"name": "Cloud Computing", "slug": "cloud"}
        ]
        
        created = []
        for data in subjects:
            subject, _ = Subject.objects.get_or_create(
                name=data["name"],
                defaults={"slug": data["slug"], "is_active": True}
            )
            created.append(subject)
        
        print(f"✔ Created {len(created)} subjects")
        return created

    def create_instructors(self, User):
        instructors = []
        social_domains = {
        'facebook': 'https://facebook.com/{}',
        'twitter': 'https://twitter.com/{}',
        'instagram': 'https://instagram.com/{}',
        'linkedin': 'https://linkedin.com/in/{}'
        }

        for i in range(1, 14):  # Create instructors
            try:
                email = f"instructor_{i}_{fake.unique.email()}"
                username = f"prof_{fake.unique.user_name()}"

                instructor = User.objects.create_user(
                    email=email,
                    username=username,
                    password='testpass123',
                    is_instructor=True,
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )

                # Add random social media URLs (2-3 per instructor)
                social_platforms = random.sample(
                    list(social_domains.keys()), 
                    k=random.randint(2, 3)
                )
            
                for platform in social_platforms:
                    url = social_domains[platform].format(username)
                    setattr(instructor, f"{platform}_url", url)
            
                instructor.save()
            
                avatar_url = f"https://i.pravatar.cc/300?u={email}" 
                if not self.download_image(avatar_url, instructor.avatar):
                    print(f"⚠ Could not set avatar for instructor {i}")

                instructors.append(instructor)
            except IntegrityError:
                continue  
    
        print(f"✔ Created {len(instructors)} instructors")
        return instructors

    def create_subcategories(self, subjects):
        subcategories = []
        category_types = [
        "Fundamentals", "Advanced Concepts", "Practical Applications",
        "Certification Prep", "Project-Based", "Case Studies",
        "Tools & Frameworks", "Best Practices", "Emerging Trends"
        ]

        for subject in subjects:
        # Select 3-5 random category types for each subject
            selected_types = random.sample(category_types, k=random.randint(3,5))
        
            for cat_type in selected_types:
                subcat = CourseCategory.objects.create(
                    subject=subject,
                    name=f"{cat_type} in {subject.name}",
                    slug=slugify(f"{subject.slug}-{cat_type}")
                )
                subcategories.append(subcat)
    
        print(f"✔ Created {len(subcategories)} subcategories")
        return subcategories

    def create_tags(self, instructors):
        tags = [
            "Beginner", "Intermediate", "Advanced",
            "Project-Based", "Certification", "Hands-On",
            "Theory", "Practical", "Workshop",
            "Case Study", "Exam Prep", "Industry Standard"
        ]
        
        created = []
        for tag_name in tags:
            tag = Tag.objects.create(
            name=tag_name,
            Created_by=random.choice(instructors) 
        )  
        created.append(tag)  
    
        print(f"✔ Created {len(created)} tags")
        return created

    def create_courses(self, subcategories, instructors, tags):
        courses = []
        tech_keywords = {
        "Data Science": "data,science,python,analysis",
        "Web Development": "web,code,development,programming",
        "Artificial Intelligence": "ai,machine,learning,robot",
        "Cybersecurity": "security,hacking,network,encryption",
        "Mobile Development": "mobile,app,ios,android",
        "Cloud Computing": "cloud,server,aws,azure"
        }

        course_templates = [
        "Mastering {topic}",
        "{topic} for {level} Developers",
        "The Complete {topic} Guide",
        "{topic} Fundamentals",
        "Advanced {topic} Techniques",
        "Practical {topic} Applications",
        "{topic} Projects Workshop"
        ]

        for subcat in subcategories:
            theme = tech_keywords.get(subcat.subject.name, "technology,education")
            subject_keyword = subcat.subject.name.split()[0]  # Get first word of subject
        
            for i in range(random.randint(2,4)):
                # Generate more independent course title
                template = random.choice(course_templates)
                topic = fake.word(ext_word_list=[
                    "Python", "JavaScript", "Machine Learning", 
                    "Web Security", "Mobile UX", "Cloud Architecture",
                    "Data Analysis", "AI Models", "DevOps"
            ])

            level = random.choice(['Beginner', 'Intermediate', 'Professional'])
            course_title = template.format(topic=topic, level=level)

            course = Course.objects.create(
                title=course_title,
                description=fake.paragraph(nb_sentences=5),
                category=subcat,
                instructor=random.choice(instructors),
                price=random.choice([29.99, 49.99, 79.99]),
                level=random.choice(['BG', 'IM', 'AD']),
                is_published=True,
                applications_covered=", ".join(fake.words(nb=3)),
                thumbnail=''
            )
                
                # Download and set thumbnail
            thumbnail_url = f"https://picsum.photos/800/450?{theme}&{i}"
            self.download_image(thumbnail_url, course.thumbnail)
                
                # Add tags
            if len(tags) >= 2:
                course.tags.set(random.sample(tags, random.randint(1, 2)))
            elif tags:  # If we only have 1 tag
                course.tags.add(tags[0])
                
                total_minutes = 0
            for lesson_num in range(1, 7):
                lesson_duration = random.randint(20, 60)
                Lesson.objects.create(
                    course=course,
                    title=f"Module {lesson_num}: {fake.sentence(nb_words=3)}",
                    order=lesson_num,
                    content=fake.paragraph(nb_sentences=10),
                    video_url=f"https://lectures.school/{slugify(course.title)}-{lesson_num}",
                    duration=timedelta(minutes=lesson_duration),
                    is_free=(lesson_num == 1)
                )
                total_minutes += lesson_duration
            
            # Update course duration (convert minutes to hours)
            course.duration = round(total_minutes / 60, 1)  # Convert to hours with 1 decimal
            course.save()
            
            courses.append(course)
    
        print(f"✔ Created {len(courses)} courses with lessons")
        return courses

    def _enroll_and_review(self, user, courses, review_comments):
            try:
                num_courses = min(len(courses), random.randint(2, 7))
                if num_courses > 0:
                        for course in random.sample(courses, k=num_courses):

                            if hasattr(user, 'is_instructor') and user == course.instructor:
                                continue
                                
                            Enrollments.objects.create(
                                student=user,
                                Course=course
                                
                            )

                            rating = None
                            comment = None
                            created_at = None

                            if random.random() < 0.3:
                                rating = random.randint(1, 5)
                                comment = random.choice(review_comments)
                                created_at = fake.date_time_between(
                                    start_date='-1y', 
                                    end_date='now'
                                )


                                if rating:
                                    Review.objects.create(
                                        course=course,
                                        student=user,
                                        rating=rating,
                                        comment=comment,
                                        created_at=created_at
                                    )
                           

                                    course.rating_count += 1
                                    course.average_rating = (
                                    (course.average_rating * (course.rating_count - 1) + rating) 
                                    / course.rating_count
                                    )
                                    course.save()
                
            except IntegrityError:
                pass

    def create_students_and_enrollments(self, User, courses):
        students = []
        review_comments = [
            "Great course, learned a lot!",
            "The instructor was very knowledgeable",
            "Could be more practical exercises",
            "Perfect for beginners",
            "The content was a bit outdated",
            "Best course I've taken on this topic",
            "Would recommend to others",
            "Some technical issues with videos",
            "Excellent real-world examples",
            "Too theoretical for my taste"
        ]
        for i in range(1, 51):  # Create students
            try:
                email = f"student_{i}_{fake.unique.email()}"
                student = User.objects.create_user(
                    email=email,
                    username=f"student_{fake.unique.user_name()}",
                    password='testpass123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    is_instructor=False
                )
            
                avatar_url = f"https://i.pravatar.cc/300?u={email}"
                if not self.download_image(avatar_url, student.avatar):
                    print(f"⚠ Could not set avatar for student {i}")

                self._enroll_and_review(student, courses, [
                "Great course!", 
                "Very informative",
                # ... other review comments ...
            ])
                students.append(student)
            except IntegrityError:
                continue

        instructors = User.objects.filter(is_instructor=True)
        for instructor in instructors:
                    # Only enroll in courses they don't teach
                other_courses = [c for c in courses if c.instructor != instructor]
                if other_courses:
                    self._enroll_and_review(instructor, other_courses, review_comments)
                
        print(f"✔ Created {len(students)} students and enrolled instructors")
        return students

    def download_image(self, url, field):
        """Guaranteed image download with multiple fallbacks"""
        try:
            os.makedirs(os.path.dirname(field.path), exist_ok=True)
            
            # Try primary URL
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            # Save if successful
            with BytesIO(response.content) as img_data:
                field.save(f"img_{uuid.uuid4().hex[:8]}.jpg", File(img_data))
                return True
                
        except Exception as primary_error:
            print(f"⚠ Primary image failed ({url}): {primary_error}")
            
            # Fallback 1: Different image service
            try:
                fallback_url = f"https://picsum.photos/800/450?random={random.randint(1,1000)}"
                response = requests.get(fallback_url, timeout=3)
                response.raise_for_status()
                with BytesIO(response.content) as img_data:
                    field.save(f"fallback_{uuid.uuid4().hex[:8]}.jpg", File(img_data))
                    return True
                    
            except Exception as fallback_error:
                print(f"⚠ Fallback image failed: {fallback_error}")
                
                # Fallback 2: Generate solid color image programmatically
                try:
                    from PIL import Image, ImageDraw
                    color = (
                    random.randint(50, 200),
                    random.randint(50, 200),
                    random.randint(50, 200)
                )
                    img = Image.new('RGB', (800, 450), color=color)
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')
                    field.save(f"color_{uuid.uuid4().hex[:8]}.jpg", File(buffer))
                    return True
                
                except Exception as color_error:
                    print(f"⚠ Color image generation failed: {color_error}")
                    return False