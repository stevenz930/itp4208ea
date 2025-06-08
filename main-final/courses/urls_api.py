from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views_api import (
    SubjectViewSet,
    CourseCategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    ReviewViewSet
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'categories', CourseCategoryViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'lessons', LessonViewSet)

# Nested routers
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'lessons', LessonViewSet, basename='course-lessons')
courses_router.register(r'reviews', ReviewViewSet, basename='course-reviews')

urlpatterns = router.urls + courses_router.urls
