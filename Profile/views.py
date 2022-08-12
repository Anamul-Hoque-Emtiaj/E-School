from django.http import HttpResponse
from django.shortcuts import render,redirect
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
        if request.session.has_key('userid') and request.session['userid']==user_id:
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

def progress(request,user_id):
    return render(request,'progress.html')


def add_course(request,user_id):
    if request.method=='POST':
        course = request.POST
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Courses"
                        WHERE "TITLE"=%s ''', [course["title"]])
            cnt = dictfetchone(c)
            if cnt["CN"]>0:
                c.execute('''SELECT * FROM "Users"
                        WHERE "USER_ID"=%s ''', [user_id])
                user = dictfetchone(c)
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
                error = "Course with this name already exist"
                return render(request,'teacher_profile.html',  {'num_of_not':5,'user':user,'owner':1,'taken_course':taken_course, 'contributed_course': contributed_course, 'error':error})
            else:
                c.execute('''INSERT INTO "Courses"(T_ID, TITLE, DESCRIPTIONS) VALUES (%s,%s,%s)''', [user_id,course["title"],course["description"]])
                return redirect(profile,user_id)


def edit_course(request,user_id,course_id ):
    if request.method=='POST':
        course = request.POST
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT * FROM "Courses"
                         WHERE "COURSE_ID"=%s ''', [course_id])
            crs = dictfetchone(c)
            if crs["TITLE"] == course["title"]:
                c.execute('''UPDATE "Courses" SET DESCRIPTIONS = %s WHERE COURSE_ID = %s ''', [course['description'],course_id])
            else:
                c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Courses"
                        WHERE "TITLE"=%s ''', [course["title"]])
                cnt = dictfetchone(c)
                if cnt["CN"]==0:
                     c.execute('''UPDATE "Courses" SET DESCRIPTIONS = %s,TITLE = %s WHERE COURSE_ID = %s ''', [course['description'],course['title'],course_id])
    return redirect(profile,user_id)
def delete_course(request,user_id,course_id ):
    with connections['eschool_db'].cursor() as c:
        pas = request.POST["password"]
        c.execute('''SELECT PASSWORD FROM "Users" WHERE USER_ID = %s ''', [user_id])
        upas = dictfetchone(c)
        if pas == upas["PASSWORD"]:
            if request.session["role"] == 'teacher':
                c.execute('''SELECT T_ID FROM "Courses" WHERE COURSE_ID = %s ''', [course_id])
                TID = dictfetchone(c)
                if TID["T_ID"] == user_id:
                    c.callproc("DELETE_COURSE",[course_id])     
                else:
                    c.execute('''DELETE From "Contribute" WHERE T_ID = %s and C_ID = %s''', [user_id,course_id])
            elif request.session["role"] == 'student':
                c.execute('''DELETE FROM "Enrollment" WHERE COURSE_ID = %s AND S_ID = %s ''', [course_id,user_id])
    return redirect(profile,user_id)
def course_approval(request):
    return render(request,'course_approval.html')






