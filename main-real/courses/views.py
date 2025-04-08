from django.shortcuts import render,get_object_or_404, redirect
from .models import Subject, Course, CourseCategory, Lesson, Review, Enrollments,Cart, CartItem, Course, Order, OrderItem
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import random
import string

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    subjects = Subject.objects.filter(is_active=True)
    
    # Handle subject filter
    current_subject = request.GET.get('subject')
    if current_subject and current_subject != 'all':
        courses = courses.filter(category__subject__slug=current_subject)
       
        filtered_categories = CourseCategory.objects.filter(
            subject__slug=current_subject,
            course__in=courses
        ).distinct()
    else:
        
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
  
    # duration = request.GET.get('duration')
    # if duration:
        
    #     from django.db.models import Sum, F
    #     from django.db.models.functions import Coalesce
        
    #     courses = courses.annotate(
    #         total_duration=Coalesce(
    #             Sum(F('lessons__duration')), 
    #             timedelta(0)
    #         )
    #     )
        
    #     if duration == 'short':
    #         courses = courses.filter(total_duration__lte=timedelta(hours=5))
    #     elif duration == 'medium':
    #         courses = courses.filter(
    #             total_duration__gt=timedelta(hours=5),
    #             total_duration__lte=timedelta(hours=10)
    #         )
    #     elif duration == 'long':
    #         courses = courses.filter(total_duration__gt=timedelta(hours=10))
    
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
    else:  
        courses = courses.order_by('-rating_count')
    
   
    paginator = Paginator(courses, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

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

@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, is_published=True, id=course_id)
        
        
        existing_enrollment = Enrollments.objects.filter(
            student=request.user,
            Course=course
        ).exists()
        
        if not existing_enrollment:
            
            Enrollments.objects.create(
                student=request.user,
                Course=course
            )
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            messages.info(request, 'You are already enrolled in this course.')
        
        
        return redirect('course_detail', course_id=course_id)

@login_required
def my_study(request):
    enrolled_courses = Enrollments.objects.filter(
        student=request.user
    ).select_related(
        'Course',
        'Course__instructor'
    ).prefetch_related(
        'Course__reviews'
    ).order_by('-enrolled_at')

    context = {
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'my_study.html', context)

def add_to_cart(request, course_id):

    course = get_object_or_404(Course, id=course_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
 
    if CartItem.objects.filter(cart=cart, course=course).exists():
        messages.warning(request, 'This course is already in your cart')
    else:
        CartItem.objects.create(cart=cart, course=course)
        messages.success(request, 'Course added to cart successfully')
    
    return redirect('course_detail', course_id=course_id)

def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'courses/cart.html', {'cart': cart})

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Course removed from cart')
    return redirect('view_cart')

def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if request.method == 'POST':
        # Generate random order number
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=cart.total_price,
            status='completed'  # Since this is a fake payment
        )
        
        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                course=item.course,
                price=item.course.price
            )
            
            # Enroll the user in the course
            if not item.course.enrollments.filter(student=request.user).exists():
                item.course.enrollments.create(student=request.user)
        
        # Clear the cart
        cart.items.all().delete()
        
        # Send confirmation email
        send_order_confirmation(request.user, order)
        
        messages.success(request, 'Order completed successfully!')
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'courses/checkout.html', {'cart': cart})

def buy_now(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    course = get_object_or_404(Course, id=course_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Add to cart if not already there
    if not CartItem.objects.filter(cart=cart, course=course).exists():
        CartItem.objects.create(cart=cart, course=course)
    
    # Proceed directly to checkout
    return redirect('checkout')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'courses/order_confirmation.html', {'order': order})

def send_order_confirmation(user, order):
    subject = f"Your Learning Platform Order Confirmation - #{order.order_number}"
    html_message = render_to_string('courses/emails/order_confirmation.html', {
        'user': user,
        'order': order
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        'noreply@learningplatform.com',
        [user.email],
        html_message=html_message
    )