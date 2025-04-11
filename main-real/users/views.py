
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from .forms import CustomUserCreationForm, ProfileSettingsForm
from django.contrib.auth.decorators import login_required
from courses.models import Course, CourseCategory
from users.models import CustomUser
from django.http import JsonResponse

def home_view(request):
    courses = Course.objects.filter(is_published=True).distinct()
    
    courses_categories = CourseCategory.objects.distinct()
    instructors = CustomUser.objects.filter(is_instructor=True)

    context = {
        "courses": courses,
        "coursetypes": courses_categories,
        "instructors": instructors,
    }
    return render(request, 'home.html', context)

def custom_login(request):
    if request.method == 'POST':
        # Get email or username from the form
        email_or_username = request.POST.get('email') 
        password = request.POST.get('password')
        
        # First try to authenticate with email
        user = authenticate(request, email=email_or_username, password=password)
        
        # If that fails, try with username
        if user is None:
            user = authenticate(request, username=email_or_username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email/username or password")
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'registration/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.EmailOrUsernameModelBackend')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    user = request.user
    return render(request,'profile/profile.html',{'user':user})

@login_required
def setup_profile(request):
    # Check if profile already has basic info
    if request.user.username and request.user.email:
        return redirect('profile_settings')
    
    if request.method == 'POST':
        form = ProfileSetupForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_settings')
    else:
        form = ProfileSetupForm(instance=request.user)
    
    return render(request, 'setup_profile.html', {'form': form})

@login_required
def profile_settings(request):
    if request.method == 'POST':
        print("[POST]", request.POST)
        print("[FILE]", request.FILES)
        form = ProfileSettingsForm(
            data=request.POST,  
            files=request.FILES,  
            instance=request.user
        )
        #print(form)
        if form.is_valid():  
            print("Valid form")
            form.save()
            messages.success(request, 'Profile updated successfully!', extra_tags='profile_settings')
            return redirect('profile_settings')
    else:
        form = ProfileSettingsForm(instance=request.user)
    
    return render(request, 'profile/profile_settings.html', {'form': form})

def search_courses(request):
    query = request.GET.get('q', '')
    if query:
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__email__icontains=query)
        ).select_related('instructor').prefetch_related('tags').distinct()

        query_lower = query.lower()
        filtered_courses = [
            course for course in courses
            if (query_lower in course.title.lower() or
                query_lower in course.description.lower() or
                any(query_lower in tag.name.lower() for tag in course.tags.all()) or
                query_lower in course.instructor.username.lower() or
                query_lower in course.instructor.email.lower())
        ]
    else:
        filtered_courses = Course.objects.all().select_related('instructor').prefetch_related('tags')

    context = {
        'courses': filtered_courses,
        'query': query,
    }
    return render(request, 'search_results.html', context)

def autocomplete(request):
    query = request.GET.get('q', '')
    if query: 
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query) |
            Q(instructor__username__icontains=query) |
            Q(instructor__email__icontains=query),
            is_published=True
        ).select_related('instructor').prefetch_related('tags').distinct()[:10]
       
        query_lower = query.lower()
        filtered_courses = [
            course for course in courses
            if (query_lower in course.title.lower() or
                query_lower in course.description.lower() or
                any(query_lower in tag.name.lower() for tag in course.tags.all()) or
                query_lower in course.instructor.username.lower() or
                query_lower in course.instructor.email.lower())
        ][:5]

        suggestions = [
            {'title': course.title, 'instructor': f"{course.instructor.first_name} {course.instructor.last_name}"}
            for course in filtered_courses
        ]
    else:
        suggestions = []
    return JsonResponse({'suggestions': suggestions})

def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')

def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def terms_of_service(request):
    return render(request, 'pages/terms_of_service.html')

def refund_policy(request):
    return render(request, 'pages/refund_policy.html')
    
def faq(request):
    return render(request, 'pages/faq.html')

def instructor_detail(request, instructor_id):
    instructor = CustomUser.objects.filter(is_instructor=True, id=instructor_id)
    courses = Course.objects.filter(instructor=instructor_id)

    context = {
        "instructor": instructor,
        "courses": courses,
    }
    return render(request, 'instructor_detail.html', context)