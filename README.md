email: admim
pw: admin

eaBackend:
python manage.py runserver 8080

check bug:
python manage.py check
py manage.py check

check models changes:
python manage.py makemigrations
py manage.py makemigrations

change models:
python manage.py migrate
py manage.py migrate

add random data:
python manage.py generate_data
py manage.py generate_data

clean data:
python manage.py shell -c "
from django.contrib.auth import get_user_model;
from courses.models import *;
User = get_user_model();
LessonProgress.objects.all().delete();
Enrollments.objects.all().delete();
Lesson.objects.all().delete();
Course.objects.all().delete();
CourseCategory.objects.all().delete();
Subject.objects.all().delete();
Tag.objects.all().delete();
User.objects.filter(username__startswith='instructor_').delete();
User.objects.filter(username__startswith='student_').delete();
print('Deleted all test data');
"
py manage.py shell -c "
from django.contrib.auth import get_user_model;
from courses.models import *;
User = get_user_model();
LessonProgress.objects.all().delete();
Enrollments.objects.all().delete();
Lesson.objects.all().delete();
Course.objects.all().delete();
CourseCategory.objects.all().delete();
Subject.objects.all().delete();
Tag.objects.all().delete();
User.objects.filter(username__startswith='instructor_').delete();
User.objects.filter(username__startswith='student_').delete();
print('Deleted all test data');
"