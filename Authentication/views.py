from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return HttpResponse("From Home")

def login(request):
    return HttpResponse("From login")

def register_student(request):
    return HttpResponse("From register_student")

def register_teacher(request):
    return HttpResponse("From register_teacher")
    
def logout(request):
    return HttpResponse("From logout")


def all_teachers(request):
    return HttpResponse("From Profile all_teachers")

def all_students(request):
    return HttpResponse("From Profile all_students")

def all_courses(request):
    return HttpResponse("From Profile all_courses")

def search_courses(request):
    return HttpResponse("From Profile search_courses")

