from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.db import connections
import cx_Oracle

from Utils.fetcher import dictfetchall, dictfetchone

# Create your views here.
def course_details(request,course_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT * FROM "Courses"
                        WHERE "COURSE_ID"=%s ''', [course_id])
        course = dictfetchone(c)
        c.execute('''SELECT * FROM "Users","Teachers"
                    WHERE USER_ID = "Teachers".T_ID AND USER_ID in (
                    SELECT T_ID FROM "Contribute" where C_ID = %s
                    UNION
                    SELECT T_ID FROM "Courses" WHERE COURSE_ID = %s
                        ) ''', [course_id,course_id])
        teachers = dictfetchall(c)
        c.execute('''SELECT * FROM "Topics" WHERE COURSE_ID = %s ORDER BY SERIAL''', [course_id])
        topics = dictfetchall(c)
        if request.session.has_key('userid'):
            if request.session['role']=="teacher":
                c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Courses"
                        WHERE "COURSE_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                en = dictfetchone(c)
                if en["CN"] >0:
                    role = 'teacher'
                else:
                    c.execute('''SELECT COUNT(C_ID) CN FROM "Contribute"
                        WHERE "C_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                    en = dictfetchone(c)
                    if en["CN"] >0:
                        role = 'contributer'
                    else:
                        role = 'none'
            elif request.session['role']=="student":
                c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Enrollment"
                        WHERE "COURSE_ID"=%s AND "S_ID"=%s ''', [course_id,request.session['userid']])
                en = dictfetchone(c)
                if en["CN"] >0:
                    role = 'estudent'
                else:
                    role = 'student'
            else:
               role = 'none' 
        else:
            role = 'none'
    return render(request,'course_details.html',{'course':course,'role':role,'teachers':teachers,'topics':topics})

def review(request,course_id):
    return render(request,'review.html')

def forum(request,course_id):
    return render(request,'forum.html')

def topic(request,course_id,topic_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT * FROM
                    (SELECT * FROM "Contents" JOIN "Lecture" L on "Contents".CONTENT_ID = L.L_ID) FULL JOIN
                    (SELECT * FROM "Contents" JOIN "Quizs" Q on "Contents".CONTENT_ID = Q.E_ID)
                    USING (CONTENT_ID,NAME,TOPIC_ID,SERIAL,TYPE)
                    WHERE TOPIC_ID = %s
                    ORDER BY SERIAL
                    ''', [topic_id])
        contents = dictfetchall(c)
        print(contents)
        if request.session.has_key('userid'):
                if request.session['role']=="teacher":
                    c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Courses"
                            WHERE "COURSE_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                    en = dictfetchone(c)
                    if en["CN"] >0:
                        role = 'teacher'
                    else:
                        c.execute('''SELECT COUNT(C_ID) CN FROM "Contribute"
                            WHERE "C_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                        en = dictfetchone(c)
                        if en["CN"] >0:
                            role = 'contributer'
                        else:
                            role = 'none'
                elif request.session['role']=="student":
                    c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Enrollment"
                            WHERE "COURSE_ID"=%s AND "S_ID"=%s ''', [course_id,request.session['userid']])
                    en = dictfetchone(c)
                    if en["CN"] >0:
                        role = 'estudent'
                    else:
                        role = 'student'
                else:
                     role = 'none' 
        else:
                role = 'none'
    return render(request,'topic.html',{'contents':contents,'cid':course_id,'tid':topic_id,'role':role})

def content(request,course_id,topic_id,content_id):
    with connections['eschool_db'].cursor() as c:
        if request.session.has_key('userid'):
            if request.session['role']=="teacher":
                c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Courses"
                        WHERE "COURSE_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                en = dictfetchone(c)
                if en["CN"] >0:
                    role = 'teacher'
                else:
                    c.execute('''SELECT COUNT(C_ID) CN FROM "Contribute"
                        WHERE "C_ID"=%s AND "T_ID"=%s ''', [course_id,request.session['userid']])
                    en = dictfetchone(c)
                    if en["CN"] >0:
                        role = 'contributer'
                    else:
                        role = 'none'
            elif request.session['role']=="student":
                c.execute('''SELECT COUNT(COURSE_ID) CN FROM "Enrollment"
                        WHERE "COURSE_ID"=%s AND "S_ID"=%s ''', [course_id,request.session['userid']])
                en = dictfetchone(c)
                if en["CN"] >0:
                    role = 'estudent'
                else:
                    role = 'student'
            else:
               role = 'none' 
        else:
            role = 'none'
    if role=='estudent' or role=='teacher' or role=='contributer' :
        c.execute('''SELECT * FROM
                    (SELECT * FROM "Contents" JOIN "Lecture" L on "Contents".CONTENT_ID = L.L_ID) FULL JOIN
                    (SELECT * FROM "Contents" JOIN "Quizs" Q on "Contents".CONTENT_ID = Q.E_ID)
                    USING (CONTENT_ID,NAME,TOPIC_ID,SERIAL,TYPE)
                    WHERE CONTENT_ID = %s
                    ''', [content_id])
        content = dictfetchone(c)
        return render(request,'content.html',{'content':content,'cid':course_id,'tid':topic_id})
    elif role=='student':
        return redirect(course_details,course_id)
    else:
        return render(request,'login.html',{'error':'You must login first'})

def add_topic(request,course_id):
    return HttpResponse("From add_topic")

def add_video(request,topic_id):
    return HttpResponse("From add_video")

def add_quiz(request,topic_id):
    return HttpResponse("From add_quiz")

def add_question(request,content_id):
    return HttpResponse("From add_question")