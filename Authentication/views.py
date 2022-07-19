from django.db import connections
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from Utils.dictfunc import multiget
from Utils.fetcher import *

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
    if request.method=='POST':
        print(request.POST['email'])
        return render(request,'login.html',{'error':"Failed to Log in"})
    else:
        return render(request,'login.html')

def register_student(request):
    if request.method=='POST':
        return render(request,'register_student.html',{'error':"Failed to create"})
    else:
        return render(request,'register_student.html')

def register_teacher(request):
    if request.method=='POST':
        return render(request,'register_teacher.html',{'error':"Failed to create"})
    else:
        return render(request,'register_teacher.html')
    
def logout(request):
    return HttpResponse("From logout")


def all_teachers(request):
     with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Users" Where USER_ID IN (SELECT T_ID from "Teachers") ')
        users=dictfetchall(c)       
        return render(request,'all_teachers.html',{'users':users}) 

def all_students(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Users" Where USER_ID IN (SELECT S_ID from "Students") ')
        users=dictfetchall(c)       
        return render(request,'all_students.html',{'users':users}) 

def all_courses(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Courses" ')
        courses=dictfetchall(c)       
        return render(request,'all_courses.html',{'courses':courses,'userId':100,'num_of_not':5}) 

def search_courses(request):
    if request.method=='POST':
        print(request.POST['search'])
        return  redirect('/')
    else:
         return  redirect('/')

