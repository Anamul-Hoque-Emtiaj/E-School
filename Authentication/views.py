from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from Utils.fetcher import *

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
     return render(request,'login.html')

def register_student(request):
     return render(request,'register_student.html')

def register_teacher(request):
    return render(request,'register_teacher.html')
    
def logout(request):
    return HttpResponse("From logout")


def all_teachers(request):
    return render(request,'all_teachers.html')

def all_students(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Users"')
        users=dictfetchall(c)       
        print(users)
        return render(request,'all_students.html',{'users':users}) 
    #return render(request,'all_students.html')

def all_courses(request):
    return render(request,'all_courses.html')

def search_courses(request):
    return render(request,'search_courses.html')

