"""
URL configuration for learning_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.search_courses, name='search_courses'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    # path('setup-profile/', setup_profile, name='setup_profile'),
    path('profile/',views.profile,name='profile'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('instructor/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),
]