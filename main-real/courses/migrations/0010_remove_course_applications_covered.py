# Generated by Django 5.1.7 on 2025-04-08 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_remove_lesson_is_free_course_is_free_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='applications_covered',
        ),
    ]
