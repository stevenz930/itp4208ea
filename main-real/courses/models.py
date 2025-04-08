from django.db import models
from django.conf import settings
# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return self.name

class CourseCategory(models.Model):
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        related_name='categories'
    )
    name = models.CharField(max_length=50)
    slug = models.SlugField()

    class Meta:
        unique_together = ('subject', 'slug')

        def __str__(self):
            return f"{self.subject.name} > {self.name}"

class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    Created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    tags = models.ManyToManyField(Tag, blank=True)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses'
    )
    applications_covered = models.TextField( 
        blank=True,
        help_text="what app and tools will use,like Figma, Photoshop."
    )
    LEVEL_CHOICES = [
        ('BG', 'Beginner'),
        ('IM', 'Intermediate'),
        ('AD', 'Advanced'),
    ]
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='BG')
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    average_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    
    @property
    def total_duration(self):
        """Returns total course duration in hours by summing all lesson durations"""
        total_seconds = sum(
            lesson.duration.total_seconds() 
            for lesson in self.lessons.all() 
            if lesson.duration  # Only count lessons with duration set
        )
        return round(total_seconds / 3600, 1)  # Convert seconds to hours
    
    @property
    def total_duration_minutes(self):
        """Alternative: Returns total duration in minutes"""
        return sum(
            lesson.duration.total_seconds() / 60 
            for lesson in self.lessons.all() 
            if lesson.duration
        )
    
    def __str__(self):
        return self.title

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)    




    def clean(self):
        if self.student == self.course.instructor:
            raise ValidationError("Instructors cannot review their own courses")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)    
        
class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField()
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration = models.DurationField(blank=True, null=True)
    is_free = models.BooleanField(default=False)

    class Meta:
        ordering =['order']
    
    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}"

class Enrollments(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    Course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    # class Meta:
    #     unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class LessonProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', '未开始'), 
        ('started', '已开始'),
        ('completed', '已完成')
    ]
    
    enrollment = models.ForeignKey(
        Enrollments, 
        on_delete=models.CASCADE,
        related_name='lesson_progresses'
    )
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE,
        related_name='progresses'
    )
    status = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    last_viewed = models.DateTimeField(auto_now=True)
    video_progress = models.PositiveIntegerField(
        default=0,
        help_text="video progress(s)"
    )
    
    class Meta:
        unique_together = ('enrollment', 'lesson')
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title} ({self.status})"

def get_rating_counts(self):
    return {
        '5': self.reviews.filter(rating=5).count(),
        '4': self.reviews.filter(rating=4).count(),
        '3': self.reviews.filter(rating=3).count(),
        '2': self.reviews.filter(rating=2).count(),
        '1': self.reviews.filter(rating=1).count()
    }

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.course.price for item in self.items.all())

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'course')

    def __str__(self):
        return f"{self.course.title} in cart"

class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.PROTECT
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} in order #{self.order.order_number}"