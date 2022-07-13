from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home' ),
    path('login/', views.login, name='login' ),
    path('register_student', views.register_student, name='register_student' ),
    path('register_teacher', views.register_teacher, name='register_teacher' ),
    path('logout', views.logout, name='logout' ),


    path('all_students', views.all_students, name='all_students' ), #for only admin
    path('all_teachers', views.all_teachers, name='all_teachers' ),
    path('all_courses', views.all_courses, name='all_courses' ),
    path('search_courses', views.search_courses, name='search_courses' ),
]
