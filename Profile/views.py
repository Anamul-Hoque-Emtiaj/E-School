import email
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
    with connections['eschool_db'].cursor() as c:
        if request.session["role"] == "student":
            c.execute('''select * from "Users" join "Students" S on "Users".USER_ID = S.S_ID WHERE USER_ID = %s ''', [user_id])
        else:
            c.execute('''select * from "Users" JOIN "Teachers" T on "Users".USER_ID = T.T_ID WHERE USER_ID = %s ''', [user_id])
        user = dictfetchone(c)
    return render(request,'setting.html',{'user':user})

def change_password(request,user_id):
    if request.method=='POST':
        npas = request.POST["npassword"]
        cpas = request.POST["cpassword"]
        if npas == cpas:
            with connections['eschool_db'].cursor() as c:
                pas = request.POST["opassword"]
                c.execute('''SELECT PASSWORD FROM "Users" WHERE USER_ID = %s ''', [user_id])
                upas = dictfetchone(c)
                if pas == upas["PASSWORD"]:
                    c.execute('''UPDATE "Users" SET PASSWORD = %s WHERE USER_ID = %s ''', [npas,user_id])
    return redirect(setting,user_id)

def edit_info(request,user_id):
    if request.method=='POST':
        with connections['eschool_db'].cursor() as c:
            pas = request.POST["password"]
            c.execute('''SELECT PASSWORD FROM "Users" WHERE USER_ID = %s ''', [user_id])
            upas = dictfetchone(c)
            if pas == upas["PASSWORD"]:
                eml = request.POST["email"]
                c.execute('''SELECT COUNT(EMAIL) CN FROM "Users" WHERE USER_ID <> %s AND EMAIL = %s''', [user_id,eml])
                cnt = dictfetchone(c)
                if cnt["CN"] == 0:
                    name = request.POST["name"]
                    c.execute('''UPDATE "Users" SET NAME = %s ,EMAIL = %s WHERE USER_ID = %s''', [name,eml,user_id])
                    if request.session["role"] == "teacher":
                        designation = request.POST["designation"]
                        c.execute('''UPDATE "Teachers" SET DESIGNATION = %s WHERE T_ID = %s''', [designation,user_id])
    return redirect(setting,user_id)


def notification(request,user_id):
    return render(request,'notification.html')

def progress(request,user_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT E.COURSE_ID COURSE_ID
                    FROM "Courses" C, "Enrollment" E
                    WHERE C."COURSE_ID" = E."COURSE_ID" AND E."S_ID"=%s ''', [user_id])
        C_ID = dictfetchall(c)
        print(C_ID)
        for cid in C_ID:
            print(cid["COURSE_ID"])
            c.callproc('UPDATE_PROGRESS',[user_id,cid["COURSE_ID"]])
        c.execute('''SELECT *
                    FROM "Courses" C, "Enrollment" E
                    WHERE C."COURSE_ID" = E."COURSE_ID" AND E."S_ID"=%s ''', [user_id])
        courses = dictfetchall(c)
        c.execute('''SELECT * FROM "Quizs" JOIN "Contents" C2 on C2.CONTENT_ID = "Quizs".E_ID JOIN "Take_Exams" USING (E_ID) WHERE S_ID = %s ''', [user_id])
        exams = dictfetchall(c)
        print(exams)
    return render(request,'progress.html',{'courses':courses,'exams':exams})


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
            else:
                c.callproc("DELETE_COURSE",[course_id]) 
                return redirect('/all_courses/asc')
    return redirect(profile,user_id)

def approve_student(request,user_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT (SELECT NAME FROM "Users" WHERE USER_ID = E.S_ID) NAME, (SELECT TITLE FROM "Courses" WHERE E.COURSE_ID = "Courses".COURSE_ID) TITLE, ENROLL_ID ID,S_ID,COURSE_ID
                        FROM "Enrollment" E
                        WHERE ISAPPROVED = 0 AND COURSE_ID IN ((SELECT COURSE_ID FROM "Courses" WHERE T_ID = %s) UNION (SELECT C_ID FROM "Contribute" WHERE T_ID = %s)) ''', [user_id,user_id])
        enrollments = dictfetchall(c)
        print(enrollments)
    return render(request,'student_approval.html',{'enrollments':enrollments})

def accept_student(request,user_id,course_id,s_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc("APPROVED_STUDENT",[s_id,course_id])
    return redirect('/profile/'+str(request.session["userid"])+'/approve_student')
def reject_student(request,user_id,course_id,s_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc("REEJECTED_STUDENT",[s_id,course_id])
    return redirect('/profile/'+str(request.session["userid"])+'/approve_student')

def course_approval(request):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT * FROM "Courses","Users" WHERE APPROVED = 0 AND "Courses".T_ID = USER_ID ''')
        courses = dictfetchall(c)
    return render(request,'course_approval.html',{'courses':courses})

def accept_course(request,course_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('APPROVED_COURSE',[course_id])
    return redirect('/profile/admin/course_approval')

def reject_course(request,course_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('REEJECTED_COURSE',[course_id])
            
    return redirect('/profile/admin/course_approval')






