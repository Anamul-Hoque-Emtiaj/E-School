from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('<int:course_id>', views.course_details, name='course_details'),
    path('<int:course_id>/review', views.review, name='review'),
    path('<int:course_id>/forum', views.forum, name='forum'),
    path('<int:course_id>/topic/<int:topic_id>', views.topic, name='topic'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>', views.content, name='content'),

    #teacher's
    path('<int:course_id>/add_topic', views.add_topic, name='add_topic'),
    path('topic/<int:topic_id>/add_video', views.add_video, name='add_video'),
    path('topic/<int:topic_id>/add_quiz', views.add_quiz, name='add_quiz'),
    path('content/<int:content_id>/add_question', views.add_question, name='add_question'),
]
