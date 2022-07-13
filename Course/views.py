from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def course_details(request,course_id):
    return render(request,'course_details.html')

def review(request,course_id):
    return render(request,'review.html')

def forum(request,course_id):
    return render(request,'forum.html')

def topic(request,topic_id):
    return render(request,'topic.html')

def content(request,content_id):
    return render(request,'content.html')

def add_topic(request,course_id):
    return HttpResponse("From add_topic")

def add_video(request,topic_id):
    return HttpResponse("From add_video")

def add_quiz(request,topic_id):
    return HttpResponse("From add_quiz")

def add_question(request,content_id):
    return HttpResponse("From add_question")