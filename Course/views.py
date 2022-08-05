from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

from django.db import connections
import cx_Oracle

from Utils.fetcher import dictfetchone

# Create your views here.
def course_details(request,course_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT * FROM "Courses"
                        WHERE "COURSE_ID"=%s ''', [course_id])
        course = dictfetchone(c)
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
    return render(request,'course_details.html',{'course':course,'role':role})

def review(request,course_id):
    return render(request,'review.html')

def forum(request,course_id):
    return render(request,'forum.html')

def topic(request,topic_id):
    return render(request,'topic.html')

def content(request,content_id):
    return render(request,'content.html')

def add_topic(request,course_id):
    return HttpResponse("From add_topic")

def add_video(request,topic_id):
    return HttpResponse("From add_video")

def add_quiz(request,topic_id):
    return HttpResponse("From add_quiz")

def add_question(request,content_id):
    return HttpResponse("From add_question")