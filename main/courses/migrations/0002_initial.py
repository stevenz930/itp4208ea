# Generated by Django 5.1.7 on 2025-04-01 07:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taught_courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='courses.coursecategory'),
        ),
        migrations.AddField(
            model_name='enrollments',
            name='Course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course'),
        ),
        migrations.AddField(
            model_name='enrollments',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.course'),
        ),
        migrations.AddField(
            model_name='lessonprogress',
            name='enrollment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progresses', to='courses.enrollments'),
        ),
        migrations.AddField(
            model_name='lessonprogress',
            name='lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progresses', to='courses.lesson'),
        ),
        migrations.AddField(
            model_name='coursecategory',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='courses.subject'),
        ),
        migrations.AddField(
            model_name='tag',
            name='Created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, to='courses.tag'),
        ),
        migrations.AlterUniqueTogether(
            name='lessonprogress',
            unique_together={('enrollment', 'lesson')},
        ),
        migrations.AlterUniqueTogether(
            name='coursecategory',
            unique_together={('subject', 'slug')},
        ),
    ]
