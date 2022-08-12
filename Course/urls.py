from django import views
from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('<int:course_id>', views.course_details, name='course_details'),
    path('<int:course_id>/review', views.review, name='review'),
    path('<int:course_id>/forum', views.forum, name='forum'),
    path('<int:course_id>/topic/<int:topic_id>', views.topic, name='topic'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>', views.content, name='content'),

    path('<int:course_id>/enroll/<int:user_id>', views.enroll, name='enroll'),

    #teacher's
    path('<int:course_id>/add_topic', views.add_topic, name='add_topic'),
    path('<int:course_id>/remove_topic/<int:topic_id>', views.remove_topic, name='remove_topic'),
    path('<int:course_id>/edit_topic/<int:topic_id>', views.edit_topic, name='edit_topic'),
    path('<int:course_id>/up_topic/<int:topic_id>', views.up_topic, name='up_topic'),
    path('<int:course_id>/down_topic/<int:topic_id>', views.down_topic, name='down_topic'),

    path('<int:course_id>/topic/<int:topic_id>/add_lecture', views.add_lecture, name='add_lecture'),
    path('<int:course_id>/topic/<int:topic_id>/add_quiz', views.add_quiz, name='add_quiz'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/delete', views.remove_content, name='remove_content'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/edit_content', views.edit_content, name='edit_content'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/up_content', views.up_content, name='up_content'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/down_content', views.down_content, name='down_content'),

    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/prev', views.prev, name='prev'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/next', views.next, name='next'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/complete', views.complete, name='complete'),

    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/add_mcq', views.add_mcq, name='add_mcq'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/add_short', views.add_short, name='add_short'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/edit_question/<int:q_id>', views.edit_question, name='edit_question'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/delete_question/<int:q_id>', views.delete_question, name='delete_question'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/up_question/<int:q_id>', views.up_question, name='up_question'),
    path('<int:course_id>/topic/<int:topic_id>/content/<int:content_id>/down_question/<int:q_id>', views.down_question, name='down_question'),


    path('<int:course_id>/add_instructor', views.add_instructor, name='add_instructor'),
    path('<int:course_id>/remove_instructor/<int:user_id>', views.remove_instructor, name='remove_instructor'),
]
