import string
import cx_Oracle
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from Utils.HashPass import passlib_encryption, passlib_encryption_verify
from Utils.fetcher import *

# Create your views here.
def home(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * FROM "Courses" WHERE APPROVED = 1 ORDER BY RATTING DESC,NUM_OF_STUDENTS DESC,COURSE_ID ASC ')
        course1=dictfetchall(c)
        c.execute('SELECT * FROM "Courses" WHERE APPROVED = 1 ORDER BY NUM_OF_STUDENTS DESC,RATTING DESC,COURSE_ID ASC ')
        course2=dictfetchall(c)
        c.execute('SELECT * from "Users","Teachers" Where USER_ID = T_ID order by COURSE_TAKEN desc,T_ID ASC ')
        teachers=dictfetchall(c) 
    return render(request,'home.html',{'course1':course1,'course2':course2,'teachers':teachers})

def login(request):
    if request.method=='POST':
        User = request.POST
        UID = -1
        with connections['eschool_db'].cursor() as c:
            c.execute('SELECT COUNT(USER_ID) CN FROM "Users" WHERE EMAIL = %s ',[User['email']])
            res=dictfetchone(c)
            if res["CN"] == 0:
                return render(request,'login.html',{'error':'Invalid Email given'})
            c.execute('SELECT PASSWORD FROM "Users" WHERE EMAIL = %s ',[User['email']])
            res=dictfetchone(c)
            if not passlib_encryption_verify(User['password'],res["PASSWORD"]):
                return render(request,'login.html',{'error':'password didnot matched'})
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("DO_LOGIN",cx_Oracle.STRING,[User['email'],temp])
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
            if User['password'] != User['cpassword']:
                return render(request,'register_student.html',{'error':'password didnot matched'})
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("REGISTER_STUDENT",cx_Oracle.STRING,[User['name'],User['email'],passlib_encryption(User['password']),temp])
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
            if User['password'] != User['cpassword']:
                return render(request,'register_teacher.html',{'error':'password didnot matched'})
            temp = c.var(cx_Oracle.NUMBER).var
            msg = c.callfunc("REGISTER_TEACHER",cx_Oracle.STRING,[User['name'],User['email'],passlib_encryption(User['password']),User['designation'],temp])
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
        c.execute('SELECT * from "Users","Teachers" Where USER_ID = T_ID order by COURSE_TAKEN desc,T_ID ASC ')
        users=dictfetchall(c)       
        return render(request,'all_teachers.html',{'users':users}) 

def all_students(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('SELECT * from "Users","Students" Where USER_ID = S_ID ')
        users=dictfetchall(c)       
    return render(request,'all_students.html',{'users':users}) 

def all_courses(request,sortedBy):
    with connections['eschool_db'].cursor() as c:
        if sortedBy == 'popular':
            c.execute('SELECT * FROM "Courses" ORDER BY NUM_OF_STUDENTS DESC,RATTING DESC,COURSE_ID ASC ')
            courses=dictfetchall(c)  
        elif sortedBy == 'toprated':
            c.execute('SELECT * FROM "Courses" ORDER BY RATTING DESC,NUM_OF_STUDENTS DESC,COURSE_ID ASC ')
            courses=dictfetchall(c)
        else:      
            c.execute('SELECT * from "Courses" ORDER BY COURSE_ID ASC')
            courses=dictfetchall(c)
    return render(request,'all_courses.html',{'courses':courses}) 

def delete_user(request,user_id):
    with connections['eschool_db'].cursor() as c:
        pas = request.POST["password"]
        c.execute('''SELECT PASSWORD FROM "Users" WHERE USER_ID = %s ''', [request.session["userid"]])
        upas = dictfetchone(c)
        if passlib_encryption_verify(pas,upas["PASSWORD"]):
            c.execute('SELECT COUNT(S_ID) CN FROM "Students" WHERE S_ID = %s ',[user_id])
            stu=dictfetchone(c)
            c.callproc("DELETE_USER",[user_id])
            if stu["CN"]>0:
                return redirect(all_students)
            else:
                return redirect(all_teachers)
        return redirect(all_students)

def search_courses(request):
    if request.method=='POST':
        tmp = request.POST['search']
        searchkey = '%' + tmp + '%'
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT * FROM "Courses" WHERE COURSE_ID IN (
                (SELECT CF.COURSE_ID FROM "Courses" CF WHERE UPPER(CF.TITLE) LIKE UPPER(%s) OR UPPER(CF.DESCRIPTIONS) LIKE  UPPER(%s))
                UNION
                (SELECT C_ID FROM "Contribute"  WHERE "Contribute".T_ID IN ( SELECT U.USER_ID FROM "Users" U WHERE UPPER(U.NAME) LIKE UPPER(%s) OR UPPER(U.EMAIL) LIKE UPPER(%s))

                )
                UNION
                (SELECT C1.COURSE_ID FROM "Courses" C1  WHERE C1.T_ID IN ( SELECT U.USER_ID FROM "Users" U WHERE UPPER(U.NAME) LIKE UPPER(%s) OR UPPER(U.EMAIL) LIKE UPPER(%s))
                )) ''',[searchkey,searchkey,searchkey,searchkey,searchkey,searchkey])
            courses=dictfetchall(c)
            print(courses)
    return render(request,'search_courses.html',{'courses':courses}) 

