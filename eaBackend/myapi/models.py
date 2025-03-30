from django.db import models

# Create your models here.
class Lecturer(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)
    
    class Meta:
        db_table = "Lecturer"

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    brief = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Course"

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    unit = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    class Meta:
        db_table = "Lesson"
        
    def __str__(self):
        return self.title
