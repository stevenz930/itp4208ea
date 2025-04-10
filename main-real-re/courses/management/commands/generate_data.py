from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import (
    Subject, CourseCategory, Course, Tag, Lesson, Enrollments, Review,
    Order, OrderItem, Cart, CartItem, LessonProgress  
)
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
from PIL import Image, ImageDraw 
import os

fake = Faker()
User = get_user_model()

class Command(BaseCommand):
    help = 'Generates complete test data with IT-themed images and proper ID reset'

    def handle(self, *args, **options):
        print("\n=== Starting Data Generation ===")
        self.clean_test_data(User)
        subjects = self.create_subjects()
        instructors = self.create_instructors(User)
        subcategories = self.create_subcategories(subjects)
        tags = self.create_tags(instructors)
        
        # Phase 1: Create instructor-specific courses
        instructor_courses = self.create_instructor_courses(subcategories, instructors, tags)
        
        # Phase 2: Create additional subject-specific courses
        subject_courses = self.create_subject_courses(subcategories, instructors, tags)
        
        courses = instructor_courses + subject_courses
        self.create_students_and_enrollments(User, courses)

        print("\n=== Data Generation Complete ===")
        print(f"Subjects: {Subject.objects.count()}")
        print(f"Courses: {Course.objects.count()}")
        print(f"Users: {User.objects.count()}\n")

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
                    color = (
                        random.randint(50, 200),
                        random.randint(50, 200),
                        random.randint(50, 200)
                    )
                    img = Image.new('RGB', (800, 450), color=color)
                    buffer = BytesIO()
                    img.save(buffer, format='JPEG')
                    buffer.seek(0)  # Important: reset buffer position
                    field.save(f"color_{uuid.uuid4().hex[:8]}.jpg", File(buffer))
                    return True
                
                except Exception as color_error:
                    print(f"⚠ Color image generation failed: {color_error}")
                    return False

 

    def clean_test_data(self, User):
        """Delete all data in the correct order to avoid protected errors"""
        models_to_clear = [
            LessonProgress,  # Depends on Enrollments and Lesson
            Review,         # Depends on Course and User
            Enrollments,    # Depends on Course and User
            Lesson,         # Depends on Course
            OrderItem,      # Depends on Order and Course
            Order,          # Depends on User
            CartItem,       # Depends on Cart and Course
            Cart,           
            Course,         
            CourseCategory, 
            Subject,
            Tag,
        ]
        
        for model in models_to_clear:
            try:
                model.objects.all().delete()
                print(f"✔ Deleted all {model.__name__} records")
            except Exception as e:
                print(f"⚠ Error deleting {model.__name__}: {str(e)}")
                continue

        # Delete users after all other models
        User.objects.filter(username__startswith='instructor_').delete()
        User.objects.filter(username__startswith='student_').delete()

        # Reset SQLite auto-increment counters
        with connection.cursor() as cursor:
            tables = [
                'courses_lessonprogress',
                'courses_review',
                'courses_enrollments',
                'courses_lesson',
                'courses_orderitem',
                'courses_order',
                'courses_cartitem',
                'courses_cart',
                'courses_course',
                'courses_coursecategory',
                'courses_subject',
                'courses_tag',
                'users_customuser'
            ]
            for table in tables:
                try:
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
                    print(f"✔ Reset sequence for {table}")
                except Exception as e:
                    print(f"⚠ Error resetting sequence for {table}: {str(e)}")
            
            print("✔ Database cleaned and IDs reset")

    def create_subjects(self):
        subjects = [
            {"name": "Data Science", "slug": "data-science"},
            {"name": "Web Development", "slug": "web-dev"},
            {"name": "Artificial Intelligence", "slug": "ai"},
            {"name": "Cybersecurity", "slug": "cybersecurity"},
            {"name": "Mobile Development", "slug": "mobile-dev"},
            {"name": "Cloud Computing", "slug": "cloud"},
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

        universities = [
            "MIT", "Stanford", "Harvard", "UC Berkeley", "Carnegie Mellon",
            "University of Washington", "Georgia Tech", "University of Texas",
            "University of Illinois", "Caltech"
        ]

        tech_companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Facebook",
            "Netflix", "Uber", "Airbnb", "Twitter", "LinkedIn",
            "IBM", "Oracle", "Intel", "NVIDIA", "Adobe"
        ]

        for i in range(1, 14):  # Create instructors
            try:
                email = f"instructor_{i}_{fake.unique.email()}"
                username = f"prof_{fake.unique.user_name()}"
                first_name = fake.first_name()
                last_name = fake.last_name()
                
                # Create realistic bio
                grad_year = random.randint(1995, 2020)
                university = random.choice(universities)
                company = random.choice(tech_companies)
                years_exp = random.randint(5, 20)
                
                bio = f"{first_name} {last_name} graduated from {university} in {grad_year} with a degree in Computer Science. " \
                      f"Has {years_exp} years of experience working at companies like {company}. " \
                      f"Specializes in {random.choice(['backend development', 'data science', 'machine learning', 'cloud architecture', 'cybersecurity'])}. " \
                      f"Passionate about teaching and sharing knowledge with the next generation of developers."

                instructor = User.objects.create_user(
                    email=email,
                    username=username,
                    password='testpass123',
                    is_instructor=True,
                    first_name=first_name,
                    last_name=last_name,
                    bio=bio,
                    profile_public=True
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
    
        print(f"✔ Created {len(instructors)} instructors with detailed profiles")
        return instructors

    def create_subcategories(self, subjects):
        subcategories = []
        category_types = {
            "Data Science": ["Data Analysis", "Machine Learning", "Data Visualization", "Big Data", "Statistics"],
            "Web Development": ["Frontend", "Backend", "Full Stack", "Web Security", "Web Performance"],
            "Artificial Intelligence": ["Deep Learning", "Computer Vision", "NLP", "Reinforcement Learning", "AI Ethics"],
            "Cybersecurity": ["Ethical Hacking", "Network Security", "Cryptography", "Penetration Testing", "Security Analysis"],
            "Mobile Development": ["iOS", "Android", "Cross-Platform", "Mobile UI/UX", "Mobile Security"],
            "Cloud Computing": ["AWS", "Azure", "GCP", "Cloud Security", "Serverless"],
        }
        
        for subject in subjects:
            if subject.name in category_types:
                for cat_name in category_types[subject.name]:
                    subcat = CourseCategory.objects.create(
                        subject=subject,
                        name=f"{cat_name}",
                        slug=slugify(f"{subject.slug}-{cat_name}")
                    )
                    subcategories.append(subcat)
            else:
                # Fallback for any subjects not in our mapping
                subcat = CourseCategory.objects.create(
                    subject=subject,
                    name=f"{subject.name} Fundamentals",
                    slug=slugify(f"{subject.slug}-fundamentals")
                )
                subcategories.append(subcat)
    
        print(f"✔ Created {len(subcategories)} subcategories")
        return subcategories

    def create_tags(self, instructors):
        programming_tags = [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", 
            "TypeScript", "PHP", "Ruby", "Swift", "Kotlin", "Dart",
            "R", "Scala", "Perl", "Haskell", "Elixir", "Clojure"
        ]
        
        framework_tags = [
            "Django", "Flask", "React", "Angular", "Vue", "Spring",
            "Laravel", "Ruby on Rails", "Express", "ASP.NET", "TensorFlow",
            "PyTorch", "Keras", "Pandas", "NumPy", "Spark"
        ]
        
        other_tags = [
            "Beginner", "Intermediate", "Advanced", "Algorithms",
            "Data Structures", "OOP", "Functional Programming", "Design Patterns",
            "Testing", "Debugging", "Performance", "Security", "DevOps"
        ]
        
        all_tags = programming_tags + framework_tags + other_tags
        
        created = []
        for tag_name in all_tags:
            tag = Tag.objects.create(
                name=tag_name,
                Created_by=random.choice(instructors) 
            )  
            created.append(tag)  
    
        print(f"✔ Created {len(created)} programming-related tags")
        return created

    def create_instructor_courses(self, subcategories, instructors, tags):
        """First phase: Create unique courses for each instructor"""
        courses = []
        used_titles = set()
        
        tech_keywords = self._get_tech_keywords()
        course_templates = self._get_course_templates()
        programming_languages = self._get_programming_languages()
        lesson_topics = self._get_lesson_topics()
        
        for instructor in instructors:
            for attempt in range(3):  # Try 3 times per instructor
                subcat = random.choice(subcategories)
                course = self._create_unique_course(
                    subcat=subcat,
                    instructor=instructor,
                    tags=tags,
                    tech_keywords=tech_keywords,
                    course_templates=course_templates,
                    programming_languages=programming_languages,
                    lesson_topics=lesson_topics,
                    used_titles=used_titles,
                    is_instructor_course=True
                )
                if course:
                    courses.append(course)
                    used_titles.add(course.title.lower())
                    break
        
        print(f"✔ Created {len(courses)} instructor-specific courses")
        return courses

    def create_subject_courses(self, subcategories, instructors, tags):
        """Second phase: Create additional unique courses per subject"""
        courses = []
        used_titles = set()
        
        tech_keywords = self._get_tech_keywords()
        course_templates = self._get_course_templates()
        programming_languages = self._get_programming_languages()
        lesson_topics = self._get_lesson_topics()
        
        for subcat in subcategories:
            for _ in range(random.randint(1, 3)):
                for attempt in range(3):  # Try 3 times per course
                    instructor = random.choice(instructors)
                    course = self._create_unique_course(
                        subcat=subcat,
                        instructor=instructor,
                        tags=tags,
                        tech_keywords=tech_keywords,
                        course_templates=course_templates,
                        programming_languages=programming_languages,
                        lesson_topics=lesson_topics,
                        used_titles=used_titles,
                        is_instructor_course=False
                    )
                    if course:
                        courses.append(course)
                        used_titles.add(course.title.lower())
                        break
        
        print(f"✔ Created {len(courses)} subject-specific courses")
        return courses

    def _get_tech_keywords(self):
        return {
            "Data Science": "data,science,python,analysis,machine,learning",
            "Web Development": "web,development,javascript,html,css,frontend,backend",
            "Artificial Intelligence": "ai,machine,learning,neural,network",
            "Cybersecurity": "security,hacking,network,encryption,penetration",
            "Mobile Development": "mobile,app,ios,android,flutter,reactnative",
            "Cloud Computing": "cloud,aws,azure,gcp,serverless",
        }

    def _get_course_templates(self):
        return [
            "Mastering {topic} in {language}",
            "{topic} for {level} Developers",
            "The Complete {language} {topic} Guide",
            "{language} {topic} Fundamentals",
            "Advanced {topic} with {language}",
            "Practical {topic} Applications in {language}",
            "{topic} Projects with {language}",
            "Learn {language} for {topic}",
            "{language} {topic} Workshop",
            "Professional {topic} using {language}"
        ]

    def _get_programming_languages(self):
        return ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "TypeScript"]

    def _get_lesson_topics(self):
        return [
            "Introduction to {topic}",
            "{language} Basics",
            "Core Concepts",
            "Advanced Techniques",
            "Practical Examples",
            "Performance Optimization",
            "Debugging and Testing",
            "Real-world Applications",
            "Case Studies",
            "Final Project"
        ]

    def _create_unique_course(self, subcat, instructor, tags, tech_keywords, 
                            course_templates, programming_languages, lesson_topics,
                            used_titles, is_instructor_course):
        """Core method to create a guaranteed unique course"""
        theme = tech_keywords.get(subcat.subject.name, "technology,education")
        topic = subcat.name.split()[0]
        language = random.choice(programming_languages)
        
        # Generate 5 potential unique titles
        potential_titles = self._generate_potential_titles(
            subcat, course_templates, programming_languages, topic, used_titles
        )
        
        # Find first unique title
        course_title = None
        for title in potential_titles:
            if title.lower() not in used_titles:
                course_title = title
                break
        
        # Final fallback if all titles exist
        if not course_title:
            course_title = f"{potential_titles[0]} - {uuid.uuid4().hex[:4]}"
        
        # Create course with guaranteed unique title
        try:
            course = self._create_course_instance(
                course_title=course_title,
                subcat=subcat,
                instructor=instructor,
                topic=topic,
                language=language,
                is_instructor_course=is_instructor_course
            )
            
            # Set thumbnail and tags
            self._set_course_thumbnail(course, theme, language)
            self._set_course_tags(course, tags, language)
            
            # Create lessons
            self._create_course_lessons(
                course=course,
                lesson_topics=lesson_topics,
                topic=topic,
                language=language
            )
            
            return course
            
        except IntegrityError:
            return None

    def _generate_potential_titles(self, subcat, templates, languages, topic, used_titles):
        """Generate 5 potential unique title variations"""
        variations = []
        base_template = random.choice(templates)
        language = random.choice(languages)
        level = random.choice(['Beginner', 'Intermediate', 'Advanced'])
        
        specializations = {
            "Data Science": ["for Healthcare", "with Big Data", "using TensorFlow"],
            "Web Development": ["with React", "using Node.js", "for E-commerce"],
            "AI": ["for Computer Vision", "with NLP", "in Robotics"],
            "Cybersecurity": ["for Cloud", "with Kali Linux", "for Web Apps"],
            "Mobile": ["with Flutter", "using SwiftUI", "Cross-platform"],
            "Cloud": ["with AWS", "using Kubernetes", "for DevOps"]
        }
        
        # Variation 1: Base template
        variations.append(base_template.format(
            topic=topic,
            language=language,
            level=level
        ))
        
        # Variation 2: With specialization
        specialization = random.choice(specializations.get(subcat.subject.name, [""]))
        if specialization:
            variations.append(f"{base_template.format(
                topic=topic,
                language=language,
                level=level
            )}: {specialization}")
        
        # Variation 3: With year
        variations.append(f"{base_template.format(
            topic=topic,
            language=language,
            level=level
        )} ({random.choice(['2024', '2025'])})")
        
        # Variation 4: With specialization and year
        if specialization:
            variations.append(f"{base_template.format(
                topic=topic,
                language=language,
                level=level
            )}: {specialization} ({random.choice(['2024', '2025'])})")
        
        # Variation 5: Random edition
        variations.append(f"{base_template.format(
            topic=topic,
            language=language,
            level=level
        )} - {fake.word().title()} Edition")
        
        return variations

    def _create_course_instance(self, course_title, subcat, instructor, topic, language, is_instructor_course):
        """Create the actual Course instance"""
        description_intro = random.choice([
            f"This comprehensive course will teach you {topic.lower()} using {language}.",
            f"Master the art of {topic.lower()} with this {language}-based course.",
            f"A complete guide to {topic.lower()} implementation in {language}.",
            f"Learn professional {topic.lower()} techniques with {language}."
        ])
        
        description_features = random.choice([
            "\n\nWhat you'll learn:\n- Core concepts\n- Practical applications\n- Best practices",
            "\n\nCourse highlights:\n- Hands-on exercises\n- Real-world examples\n- Certificate",
            "\n\nSkills you'll gain:\n- {language} programming\n- {topic} implementation"
        ]).format(language=language, topic=topic)
        
        is_free = random.random() < 0.1 if is_instructor_course else random.random() < 0.3
        price = 0 if is_free else random.choice([19.99, 29.99, 39.99, 49.99, 79.99, 99.99])
        
        return Course.objects.create(
            title=course_title,
            description=description_intro + description_features,
            category=subcat,
            instructor=instructor,
            price=price,
            is_free=is_free,
            level=random.choice(['BG', 'IM', 'AD']),
            is_published=True,
            thumbnail=''
        )

    def _set_course_thumbnail(self, course, theme, language):
        """Download and set unique thumbnail"""
        thumbnail_url = (
            f"https://source.unsplash.com/800x450/?{theme},"
            f"{language.lower()},{random.randint(1,10000)}"
        )
        self.download_image(thumbnail_url, course.thumbnail)

    def _set_course_tags(self, course, tags, language):
        """Assign unique combination of tags"""
        selected_tags = [t for t in tags if t.name == language]
        other_tags = [t for t in tags if t.name != language]
        random.shuffle(other_tags)
        selected_tags.extend(other_tags[:min(3, len(other_tags))])
        course.tags.set(selected_tags)

    def _create_course_lessons(self, course, lesson_topics, topic, language):
        """Create unique lessons for the course"""
        total_minutes = 0
        num_lessons = random.randint(5, 10)
        used_lesson_titles = set()
        
        for lesson_num in range(1, num_lessons + 1):
            lesson_duration = random.randint(15, 90)
            
            # Generate unique lesson title
            for _ in range(3):
                current_topic = random.choice(lesson_topics).format(
                    topic=topic,
                    language=language
                )
                lesson_title = f"Module {lesson_num}: {current_topic}"
                if lesson_title not in used_lesson_titles:
                    used_lesson_titles.add(lesson_title)
                    break
            
            Lesson.objects.create(
                course=course,
                title=lesson_title,
                order=lesson_num,
                content="\n\n".join([fake.paragraph() for _ in range(3, 7)]),
                video_url=(
                    f"https://lectures.school/{slugify(course.title)}-"
                    f"{lesson_num}-{uuid.uuid4().hex[:6]}"
                ),
                duration=timedelta(minutes=lesson_duration),
            )
            total_minutes += lesson_duration
        
        course.duration = round(total_minutes / 60, 1)
        course.save()

    def _enroll_and_review(self, user, courses, review_comments):
        try:
            num_courses = min(len(courses), random.randint(1, 5))
            if num_courses > 0:
                for course in random.sample(courses, k=num_courses):
                    # Skip if user is the instructor of this course
                    if hasattr(user, 'is_instructor') and user == course.instructor:
                        continue
                        
                    # Create enrollment
                    enrollment = Enrollments.objects.create(
                        student=user,
                        Course=course,
                        enrolled_at=fake.date_time_between(
                            start_date='-1y', 
                            end_date='now'
                        )
                    )

                    # Create lesson progress for some lessons
                    for lesson in course.lessons.all()[:random.randint(1, 3)]:
                        status = random.choices(
                            ['not_started', 'started', 'completed'],
                            weights=[0.2, 0.5, 0.3]
                        )[0]
                        
                        LessonProgress.objects.create(
                            enrollment=enrollment,
                            lesson=lesson,
                            status=status,
                            video_progress=random.randint(0, 100) if status != 'not_started' else 0
                        )

                    # 30% chance to leave a review
                    if random.random() < 0.3:
                        rating = random.choices(
                            [1, 2, 3, 4, 5],
                            weights=[0.05, 0.1, 0.15, 0.3, 0.4]
                        )[0]
                        
                        Review.objects.create(
                            course=course,
                            student=user,
                            rating=rating,
                            comment=random.choice(review_comments),
                            created_at=fake.date_time_between(
                                start_date=enrollment.enrolled_at,
                                end_date='now'
                            )
                        )

                        # Update course rating stats
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
        
        universities = [
            "State University", "Community College", "Online University",
            "Tech Institute", "Liberal Arts College", "International School"
        ]
        
        companies = [
            "Tech Startup", "Local Business", "Freelance",
            "Student", "Unemployed", "Corporate Employee"
        ]

        for i in range(1, 51):  # Create students
            try:
                email = f"student_{i}_{fake.unique.email()}"
                username = f"student_{fake.unique.user_name()}"
                first_name = fake.first_name()
                last_name = fake.last_name()
                
                # Create realistic bio for students
                grad_year = random.choice([
                    str(random.randint(2015, 2023)) if random.random() > 0.3 else None,
                    "currently studying"
                ])
                
                university = random.choice(universities)
                company = random.choice(companies)
                
                bio_parts = []
                if grad_year:
                    if grad_year == "currently studying":
                        bio_parts.append(f"Currently studying Computer Science at {university}.")
                    else:
                        bio_parts.append(f"Graduated from {university} in {grad_year}.")
                
                bio_parts.append(f"Currently working as {company}.")
                bio_parts.append(f"Interested in learning {random.choice(['web development', 'data science', 'mobile apps', 'cloud computing'])}.")
                
                student = User.objects.create_user(
                    email=email,
                    username=username,
                    password='testpass123',
                    first_name=first_name,
                    last_name=last_name,
                    bio=" ".join(bio_parts),
                    profile_public=random.random() > 0.2  # 80% public profiles
                )
            
                avatar_url = f"https://i.pravatar.cc/300?u={email}"
                if not self.download_image(avatar_url, student.avatar):
                    print(f"⚠ Could not set avatar for student {i}")

                self._enroll_and_review(student, courses, review_comments)
                students.append(student)
            except IntegrityError:
                continue

        # Enroll instructors in courses they don't teach
        instructors = User.objects.filter(is_instructor=True)
        for instructor in instructors:
            other_courses = [c for c in courses if c.instructor != instructor]
            if other_courses:
                self._enroll_and_review(instructor, other_courses, review_comments)
                
        print(f"✔ Created {len(students)} students with realistic profiles")
        return students

