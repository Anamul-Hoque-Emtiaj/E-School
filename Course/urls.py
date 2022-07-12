from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('<int:course_id>/', views.course_details ),
]
