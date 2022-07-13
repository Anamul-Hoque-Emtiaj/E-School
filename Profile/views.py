from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def profile(request,user_id):
    return HttpResponse("From Profile")

def setting(request,user_id):
    return HttpResponse("From Profile setting")

def notification(request,user_id):
    return HttpResponse("From Profile notification")

def enrolled_course(request,user_id):
    return HttpResponse("From Profile enrolled_course")

def progress(request,user_id):
    return HttpResponse("From Profile progress")

def taken_course(request,user_id):
    return HttpResponse("From Profile taken_course")

def taken_course(request,user_id):
    return HttpResponse("From Profile taken_course")

def add_course(request,user_id):
    return HttpResponse("From Profile add_course")

def course_approval(request):
    return HttpResponse("From Profile course_approval")





