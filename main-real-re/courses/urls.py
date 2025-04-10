# courses/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('course_list/', views.course_list, name='course_list'),
    path('detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
     path('course/<int:course_id>/review/', views.submit_review, name='submit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('my-study/', views.my_study, name='my_study'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('buy-now/<int:course_id>/', views.buy_now, name='buy_now'),
    
]