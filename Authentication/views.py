from asyncio.windows_events import NULL
import string
import cx_Oracle
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from Utils.dictfunc import multiget
from Utils.fetcher import *

# Create your views here.
def home(request):
    return render(request,'home.html')

def login(request):
    if request.method=='POST':
        User = request.POST
        UID = -1
        with connections['eschool_db'].cursor() as c:
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("DO_LOGIN",cx_Oracle.STRING,[User['email'],User['password'],temp])
            UID = int(temp.getvalue())
            print(msg,UID)
        if UID==-1:
            return render(request,'login.html',{'error':msg})
        else:
            if request.session.has_key('userid'):
                del request.session['userid']
                del request.session['role']
            request.session['userid'] = UID
            request.session['role'] = msg
            return redirect('profile',user_id=UID)
    else:
        return render(request,'login.html')

def register_student(request):
    if request.method=='POST':
        User = request.POST
        SID = -1
        with connections['eschool_db'].cursor() as c:
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("REGISTER_STUDENT",cx_Oracle.STRING,[User['name'],User['email'],User['password'],User['cpassword'],temp])
            SID = int(temp.getvalue())
            print(msg,SID)
        if SID==-1:
            return render(request,'register_student.html',{'error':msg})
        else:
            if request.session.has_key('userid'):
                del request.session['userid']
                del request.session['role']
            request.session['userid'] = SID
            request.session['role'] = 'student'
            #return redirect(f'profile/{SID}')
            return redirect('profile',user_id=SID)
    else:
        return render(request,'register_student.html')

def register_teacher(request):
    if request.method=='POST':
        User = request.POST
        TID = -1
        with connections['eschool_db'].cursor() as c:
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("REGISTER_TEACHER",cx_Oracle.STRING,[User['name'],User['email'],User['password'],User['cpassword'],User['designation'],temp])
            TID = int(temp.getvalue())
            print(msg,TID)
        if TID==-1:
            return render(request,'register_teacher.html',{'error':msg})
        else:
            if request.session.has_key('userid'):
                del request.session['userid']
                del request.session['role']
            request.session['userid'] = TID
            request.session['role'] = 'teacher'
            #return redirect(f'profile/{TID}')
            return redirect('profile',user_id=TID)
    else:
        return render(request,'register_teacher.html')
    
def logout(request):
    if request.session.has_key('userid'):
        del request.session['userid']
        del request.session['role']
    return redirect('home')


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

def all_courses(request,sortedBy):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Courses" ')
        courses=dictfetchall(c)       
    return render(request,'all_courses.html',{'courses':courses}) 

def search_courses(request):
    if request.method=='POST':
        print(request.POST['search'])
        return  redirect('/')
    else:
         return  redirect('/')

