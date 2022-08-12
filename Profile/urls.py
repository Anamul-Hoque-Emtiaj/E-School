from django import views
from django.urls import path
from . import views

urlpatterns = [
    #common
    path('<int:user_id>', views.profile, name='profile' ),
    path('<int:user_id>/setting', views.setting, name='setting' ),
    path('<int:user_id>/notification', views.notification, name='notification' ),

    #student's
    path('<int:user_id>/progress', views.progress, name='progress' ),

    #teacher's
    path('<int:user_id>/add_course', views.add_course, name='add_course' ),
    path('<int:user_id>/edit_course/<int:course_id>', views.edit_course, name='edit_course' ),
    path('<int:user_id>/delete_course/<int:course_id>', views.delete_course, name='delete_course' ),


    #admin
    path('admin/course_approval', views.course_approval, name='course_approval' ),

]
