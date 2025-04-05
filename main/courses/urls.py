# courses/urls.py
from django.urls import path
from . import views
from .views import course_list
# from .views import courses

urlpatterns = [
    path('course_list/', course_list, name='course_list'),
]