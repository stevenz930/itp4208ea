# courses/urls.py
from django.urls import path
from . import views
from .views import course_list, course_detail
# from .views import courses

urlpatterns = [
    path('course_list/', course_list, name='course_list'),
    path('detail/<int:course_id>/', course_detail, name='course_detail'),
]