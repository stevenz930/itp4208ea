from django.contrib import admin
from .models import Subject, CourseCategory, Course, Lesson, Enrollments, Order

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'slug')
    list_filter = ('subject',)  
    
    def get_subject(self, obj):
        return obj.subject.name
    get_subject.short_description = 'Subject'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'level', 'is_published')
    list_filter = ('category', 'level', 'is_published')
    filter_horizontal = ('tags',)
    search_fields = ('title', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','order_number','status','user_id')
