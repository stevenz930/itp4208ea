from django.shortcuts import render,get_object_or_404
from .models import Subject, Course, CourseCategory, Lesson, Review, Enrollments
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    subjects = Subject.objects.filter(is_active=True)
    
    # Handle subject filter
    current_subject = request.GET.get('subject')
    if current_subject and current_subject != 'all':
        courses = courses.filter(category__subject__slug=current_subject)
        # Get categories for the current subject
        filtered_categories = CourseCategory.objects.filter(
            subject__slug=current_subject,
            course__in=courses
        ).distinct()
    else:
        # Get all categories if no subject is selected
        filtered_categories = CourseCategory.objects.filter(
            course__in=courses
        ).distinct()



    # Handle multiple category selections
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        courses = courses.filter(category__id__in=selected_categories)
    
    # Handle level filter
    selected_levels = request.GET.getlist('level')
    if selected_levels:
        courses = courses.filter(level__in=selected_levels)
    
    # Handle duration filter
  
    duration = request.GET.get('duration')
    if duration:
        # We need to annotate the duration to filter on it
        from django.db.models import Sum, F
        from django.db.models.functions import Coalesce
        
        courses = courses.annotate(
            total_duration=Coalesce(
                Sum(F('lessons__duration')), 
                timedelta(0)
            )
        )
        
        if duration == 'short':
            courses = courses.filter(total_duration__lte=timedelta(hours=5))
        elif duration == 'medium':
            courses = courses.filter(
                total_duration__gt=timedelta(hours=5),
                total_duration__lte=timedelta(hours=10)
            )
        elif duration == 'long':
            courses = courses.filter(total_duration__gt=timedelta(hours=10))
    
    # Handle sorting
    sort = request.GET.get('sort', 'popular')
    if sort == 'highest':
        courses = courses.order_by('-average_rating')
    elif sort == 'newest':
        courses = courses.order_by('-created_at')
    elif sort == 'price_low':
        courses = courses.order_by('price')
    elif sort == 'price_high':
        courses = courses.order_by('-price')
    else:  # default is popular
        courses = courses.order_by('-rating_count')
    
    # Pagination - 9 courses per page
    paginator = Paginator(courses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get available filter options
    available_categories = CourseCategory.objects.filter(
        id__in=Course.objects.filter(is_published=True).values('category'))
    
    context = {
        'courses': page_obj,
        'filtered_categories': filtered_categories,
        'all_categories': CourseCategory.objects.filter(course__in=courses).distinct(),
        'level_choices': Course.LEVEL_CHOICES,
        'current_sort': sort,
        'current_subject': current_subject,
        'subjects': subjects,
    }
    return render(request, 'course_list.html', context)



def course_detail(request, course_id):

    course = get_object_or_404(Course, is_published=True, id=course_id)
    
    # Efficiently fetch related data
    lessons = Lesson.objects.filter(course=course).order_by('order')
    reviews = Review.objects.select_related('student').filter(course=course).order_by('-created_at')
    
 
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollments.objects.filter(
            student=request.user,
            Course=course
        ).exists()

    context = {
        "course": course,
        "lessons": lessons,
        "reviews": reviews,
        "is_enrolled": is_enrolled,
    }
    return render(request, 'course_detail.html', context)