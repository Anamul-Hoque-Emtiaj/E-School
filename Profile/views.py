from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

from django.db import connections
import cx_Oracle

from Utils.fetcher import dictfetchall, dictfetchone
from datetime import date

# Create your views here.
def profile(request,user_id):
    with connections['eschool_db'].cursor() as c:
        msg = c.callfunc("CHECK_USER",cx_Oracle.STRING,[user_id])
        print(msg,user_id)
        if msg!='Invalid User':
            c.execute('''SELECT * FROM "Users"
                        WHERE "USER_ID"=%s ''', [user_id])
            user = dictfetchone(c)
    ownProfile = 0
    if request.session['userid']==user_id:
        ownProfile = 1
    
    if msg=='student':
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT * FROM "Students"
                        WHERE "S_ID"=%s ''', [user_id])
            student = dictfetchone(c)
            user["NOC"] = student["COURSE_ENROLLED"]
            user["role"] = "Student"

            c.execute('''SELECT *
                    FROM "Courses" C, "Enrollment" E
                    WHERE C."COURSE_ID" = E."COURSE_ID" AND E."S_ID"=%s ''', [user_id])
            courses = dictfetchall(c)
            #courses["Date"] = today - courses["Date"].date()
            print(courses)
        return render(request,'student_profile.html', {'num_of_not':5,'user':user,'owner':ownProfile,'courses':courses})
    elif msg=='teacher':
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT * FROM "Teachers"
                        WHERE "T_ID"=%s ''', [user_id])
            TEACHER = dictfetchone(c)
            user["NOC"] = TEACHER["COURSE_TAKEN"]
            user["DESIGNATION"] = TEACHER["DESIGNATION"]

            c.execute('''SELECT * FROM "Courses"
                        WHERE "T_ID"=%s ''', [user_id])
            taken_course = dictfetchall(c)

            c.execute('''SELECT * FROM "Courses"
                        WHERE "COURSE_ID" IN (SELECT C_ID FROM "Contribute"
                        WHERE "T_ID"=%s) ''', [user_id])
            contributed_course = dictfetchall(c)
            user["role"] = "Teacher"
        return render(request,'teacher_profile.html',  {'num_of_not':5,'user':user,'owner':ownProfile,'taken_course':taken_course, 'contributed_course': contributed_course})
    elif msg=='admin':
        user["role"] = "Admin"
        return render(request,'admin_profile.html',  {'num_of_not':5,'user':user,'owner':ownProfile})
    else:
        return render(request,'login.html',{'error':'Invalid UserID'})


def setting(request,user_id):
    return render(request,'setting.html')


def notification(request,user_id):
    return render(request,'notification.html')


def enrolled_course(request,user_id):
    return render(request,'enrolled_course.html')

def progress(request,user_id):
    return render(request,'progress.html')


def taken_course(request,user_id):
    return render(request,'taken_course.html')


def add_course(request,user_id):
    return HttpResponse("From Profile add_course")

def course_approval(request):
    return render(request,'course_approval.html')






