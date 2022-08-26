from tokenize import Double
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
        if course["APPROVED"] == 1:
            c.execute('''SELECT * FROM "Users","Teachers"
                        WHERE USER_ID = "Teachers".T_ID AND USER_ID in (
                        SELECT T_ID FROM "Contribute" where C_ID = %s
                        UNION
                        SELECT T_ID FROM "Courses" WHERE COURSE_ID = %s
                            ) ''', [course_id,course_id])
            teachers = dictfetchall(c)
            c.execute('''SELECT * FROM "Topics" WHERE COURSE_ID = %s ORDER BY SERIAL''', [course_id])
            topics = dictfetchall(c)
            c.execute('''SELECT * FROM "Feedback" join "Users" ON S_ID = USER_ID WHERE C_ID = %s''', [course_id])
            reviews = dictfetchall(c)
            feedback = 'no'
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
                        c.execute('''SELECT ISAPPROVED FROM "Enrollment"
                            WHERE "COURSE_ID"=%s AND "S_ID"=%s ''', [course_id,request.session['userid']])
                        en = dictfetchone(c)
                        if en["ISAPPROVED"]==1:
                            role = 'estudent'
                            c.execute('''SELECT COUNT(S_ID) CN FROM "Feedback" WHERE C_ID = %s AND S_ID = %s ''', 
                                    [course_id,request.session['userid']])
                            cn = dictfetchone(c)
                            if cn["CN"]==0:
                                feedback = 'yes'
                            else:
                                feedback = 'done'
                        else:
                            role = 'pstudent'
                    else:
                        role = 'student'
                else:
                    role = 'none' 
            else:
                role = 'none'
            return render(request,'course_details.html',{'course':course,'role':role,'teachers':teachers,'topics':topics,'reviews':reviews,'feedback':feedback})
        else:
            return redirect('/profile/'+str(course["T_ID"])+'')

def forum(request,course_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT * FROM "Forums" JOIN "Users" U on U.USER_ID = "Forums".U_ID WHERE C_ID = %s ORDER BY F_ID DESC
                    ''', [course_id])
        comments = dictfetchall(c)
    return render(request,'forum.html',{'comments':comments,'cid':course_id})
def add_comment(request,course_id):
    des = request.POST["comment_text"]
    print(des)
    with connections['eschool_db'].cursor() as c:
        c.execute('''INSERT INTO "Forums"(C_ID, U_ID, DESCRIPTION) VALUES (%s,%s,%s)
                    ''', [course_id,request.session["userid"],des])
    return redirect('/course/'+str(course_id)+'/forum')
def add_reply(request,course_id,forum_id):
    des = request.POST["reply"]
    with connections['eschool_db'].cursor() as c:
        c.execute('''INSERT INTO "Forums"(C_ID, U_ID, PAR_COM_ID, DESCRIPTION) VALUES (%s,%s,%s,%s)
                    ''', [course_id,request.session["userid"],forum_id,des])
        c.execute('''UPDATE "Forums" SET CHILD = CHILD + 1 WHERE F_ID = %s
                    ''', [forum_id])
    return redirect('/course/'+str(course_id)+'/forum')
def edit_comment(request,course_id,forum_id):
    des = request.POST["description"]
    with connections['eschool_db'].cursor() as c:
        c.execute('''UPDATE "Forums" SET DESCRIPTION = %s WHERE F_ID = %s
                    ''', [des,forum_id])
    return redirect('/course/'+str(course_id)+'/forum')
def delete_comment(request,course_id,forum_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc("DELETE_FORUM",[forum_id])
    return redirect('/course/'+str(course_id)+'/forum')

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
                    c.execute('''SELECT ISAPPROVED FROM "Enrollment"
                            WHERE "COURSE_ID"=%s AND "S_ID"=%s ''', [course_id,request.session['userid']])
                    en = dictfetchone(c)
                    if en["ISAPPROVED"]==1:
                        role = 'estudent'
                    else:
                        role = 'pstudent'
                else:
                    role = 'student'
            else:
               role = 'admin' 
        else:
            role = 'none'
        if role=='estudent' or role=='teacher' or role=='contributer' or role=='admin':
            c.execute('''SELECT * FROM
                        (SELECT * FROM "Contents" JOIN "Lecture" L on "Contents".CONTENT_ID = L.L_ID) FULL JOIN
                        (SELECT * FROM "Contents" JOIN "Quizs" Q on "Contents".CONTENT_ID = Q.E_ID)
                        USING (CONTENT_ID,NAME,TOPIC_ID,SERIAL,TYPE)
                        WHERE CONTENT_ID = %s
                        ''', [content_id])
            content = dictfetchone(c)
            if content["TYPE"] == 'lecture':
                status = 'pending'
                c.execute('''SELECT COUNT(S_ID) CN FROM "Completion" WHERE S_ID = %s AND L_ID = %s
                         ''', [request.session['userid'],content_id])
                cur = dictfetchone(c)
                if cur["CN"]>0:
                    status = 'completed'
                return render(request,'content.html',{'content':content,'cid':course_id,'tid':topic_id,'role':role,'status':status})
            else:
                c.execute('''SELECT * FROM
                        "Questions"
                        WHERE E_ID = %s
                        ORDER BY SERIAL
                        ''', [content_id])
                questions = dictfetchall(c)
                if role=='teacher' or role=='contributer' or role=='admin': 
                    return render(request,'quiz.html',{'content':content,'cid':course_id,'tid':topic_id,'role':role,'questions':questions})
                else:
                    status = 'pending'
                    c.execute('''SELECT COUNT(S_ID) CN FROM "Take_Exams" WHERE S_ID = %s AND E_ID = %s
                         ''', [request.session['userid'],content_id])
                    cur = dictfetchone(c)
                    obtainMark = -1
                    if cur["CN"]>0:
                        c.execute('''SELECT OBTAINED_MARKS FROM "Take_Exams" WHERE S_ID = %s AND E_ID = %s
                         ''', [request.session['userid'],content_id])
                        cur = dictfetchone(c)
                        obtainMark = cur["OBTAINED_MARKS"]

                        if obtainMark*2>=content["MARKS"]:
                            status = 'completed'
                        else:
                            status = 'failed'
                    return render(request,'give_exam.html',{'content':content,'cid':course_id,'tid':topic_id,'role':role,'questions':questions,'obtainMark':obtainMark,'status':status})
        elif role=='student' or role=='pstudent':
            return redirect('/course/'+str(course_id)+'')
        else:
            return render(request,'login.html',{'error':'You must login first'})

def enroll(request,course_id,user_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''INSERT INTO "Enrollment"(S_ID, COURSE_ID) VALUES (%s,%s)
                        ''', [user_id,course_id])
    return redirect('/course/'+str(course_id)+'')

def add_instructor(request,course_id):
    if request.method=='POST':
        email = request.POST["email"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT COUNT(USER_ID) CN  FROM "Users","Teachers" WHERE T_ID = "Users".USER_ID AND EMAIL = %s
                        ''', [email])
            cnt = dictfetchone(c)
            if cnt["CN"]==1:
                c.execute('''SELECT USER_ID FROM "Users" WHERE EMAIL = %s
                        ''', [email])
                uid = dictfetchone(c)
                c.execute('''INSERT INTO "Contribute"(T_ID, C_ID) VALUES (%s,%s)
                        ''', [uid["USER_ID"],course_id])
    return redirect('/course/'+str(course_id)+'')

def remove_instructor(request,course_id,user_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''DELETE FROM "Contribute" WHERE C_ID = %s AND T_ID = %s
                ''', [course_id,user_id])
    return redirect('/course/'+str(course_id)+'')
def remove_topic(request,course_id,topic_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('DELETE_TOPIC',[topic_id])
    return redirect('/course/'+str(course_id)+'')

def add_topic(request,course_id):
    if request.method=='POST':
        title = request.POST["name"]
        description = request.POST["description"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''INSERT INTO "Topics"(TOPIC_NAME, TOPIC_DESCRIPTIONS, COURSE_ID) VALUES (%s,%s,%s)
                        ''', [title,description,course_id])
    return redirect('/course/'+str(course_id)+'')

def edit_topic(request,course_id,topic_id):
    if request.method=='POST':
        title = request.POST["name"]
        description = request.POST["description"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''UPDATE "Topics" SET TOPIC_NAME = %s,TOPIC_DESCRIPTIONS = %s WHERE TOPIC_ID = %s
                        ''', [title,description,topic_id])
    return redirect('/course/'+str(course_id)+'')
def up_topic(request,course_id,topic_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('UP',[topic_id,course_id,'T'])
        
    return redirect('/course/'+str(course_id)+'')
def down_topic(request,course_id,topic_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('DOWN',[topic_id,course_id,'T'])
        
    return redirect('/course/'+str(course_id)+'')

def add_lecture(request,course_id,topic_id):
    if request.method=='POST':
        title = request.POST["title"]
        description = request.POST["description"]
        duration = request.POST["duration"]
        link = request.POST["link"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''INSERT INTO "Contents"(NAME, TOPIC_ID, TYPE) VALUES (%s, %s, %s)
                        ''', [title,topic_id,'lecture'])
            c.execute('''select CONTENT_ID from "Contents" where TOPIC_ID = %s and NAME = %s and TYPE = %s
                        ''', [topic_id,title,'lecture'])
            en = dictfetchone(c)
            c.execute('''insert into "Lecture"(L_ID, DESCRIPTION, VIDEO_LINK, DURATION) VALUES (%s,%s,%s,%s)
                        ''', [en["CONTENT_ID"],description,link,duration])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))

def add_quiz(request,course_id,topic_id):
    if request.method=='POST':
        title = request.POST["title"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''INSERT INTO "Contents"(NAME, TOPIC_ID, TYPE) VALUES (%s, %s, %s)
                        ''', [title,topic_id,'exam'])
            c.execute('''select CONTENT_ID from "Contents" where TOPIC_ID = %s and NAME = %s and TYPE = %s
                        ''', [topic_id,title,'exam'])
            en = dictfetchone(c)
            c.execute('''INSERT INTO "Quizs"(E_ID) VALUES (%s)
                        ''', [en["CONTENT_ID"]])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))

def remove_content(request,course_id,topic_id,content_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('DELETE_CONTENT',[content_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))

def edit_content(request,course_id,topic_id,content_id):
    if request.method=='POST':
        title = request.POST["title"]
       
        with connections['eschool_db'].cursor() as c:
            c.execute('''UPDATE "Contents" SET NAME = %s WHERE CONTENT_ID = %s
                        ''', [title,content_id])
            c.execute('''select TYPE FROM "Contents" WHERE CONTENT_ID = %s
                        ''', [content_id])
            en = dictfetchone(c)
            if en["TYPE"] == "lecture":
                description = request.POST["description"]
                duration = request.POST["duration"]
                link = request.POST["link"]
                c.execute('''UPDATE "Lecture" SET DESCRIPTION = %s, DURATION = %s, VIDEO_LINK = %s WHERE L_ID = %s
                            ''', [description,duration,link,content_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))

def up_content(request,course_id,topic_id,content_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('UP',[content_id,topic_id,'C'])
        
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))
def down_content(request,course_id,topic_id,content_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('DOWN',[content_id,topic_id,'C'])
        
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id))

def prev(request,course_id,topic_id,content_id):
    cid = content_id
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT SERIAL FROM "Contents" WHERE CONTENT_ID = %s
                        ''', [content_id])
        cur = dictfetchone(c)
        s1 = cur["SERIAL"]
        c.execute(''' SELECT COUNT(CONTENT_ID) CNT FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL < %s
                        ''', [topic_id,s1])
        cur = dictfetchone(c)
        cnt = cur["CNT"]
        if cnt>0:
            c.execute(''' SELECT MAX(SERIAL) MXS FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL < %s
                        ''', [topic_id,s1])
            cur = dictfetchone(c)
            s2 = cur["MXS"]
            c.execute(''' SELECT CONTENT_ID FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL = %s
                        ''', [topic_id,s2])
            cur = dictfetchone(c)
            cid = cur["CONTENT_ID"]
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(cid))

def next(request,course_id,topic_id,content_id):
    cid = content_id
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT SERIAL FROM "Contents" WHERE CONTENT_ID = %s
                        ''', [content_id])
        cur = dictfetchone(c)
        s1 = cur["SERIAL"]
        c.execute(''' SELECT COUNT(CONTENT_ID) CNT FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL > %s
                        ''', [topic_id,s1])
        cur = dictfetchone(c)
        cnt = cur["CNT"]
        if cnt>0:
            c.execute(''' SELECT MIN(SERIAL) MNS FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL > %s
                        ''', [topic_id,s1])
            cur = dictfetchone(c)
            s2 = cur["MNS"]
            c.execute(''' SELECT CONTENT_ID FROM "Contents" WHERE TOPIC_ID = %s AND SERIAL = %s
                        ''', [topic_id,s2])
            cur = dictfetchone(c)
            cid = cur["CONTENT_ID"]
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(cid))

def complete(request,course_id,topic_id,content_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT COUNT(*) CN FROM "Completion" WHERE S_ID = %s AND L_ID = %s
                        ''', [request.session["userid"],content_id])
        cnt = dictfetchone(c)
        if cnt["CN"]==0:
            c.execute('''INSERT INTO "Completion"VALUES (%s,%s)
                            ''', [request.session["userid"],content_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id)+'/next')

def add_mcq(request,course_id,topic_id,content_id):
    if request.method=='POST':
        with connections['eschool_db'].cursor() as c:
            question = request.POST["question"]
            op1 = request.POST["op1"]
            op2 = request.POST["op2"]
            op3 = request.POST["op3"]
            op4 = request.POST["op4"]
            ra = request.POST["ra"]
            mark = request.POST["mark"]
            c.execute('''INSERT INTO "Questions"(E_ID, QUESTION, OP1, OP2, OP3, OP4, RA,NUM, TYPE)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ''', [content_id,question,op1,op2,op3,op4,ra,mark,'mcq'])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))

def add_short(request,course_id,topic_id,content_id):
    if request.method=='POST':
        with connections['eschool_db'].cursor() as c:
            question = request.POST["question"]
            ra = request.POST["ra"]
            mark = request.POST["mark"]
            c.execute('''INSERT INTO "Questions"(E_ID, QUESTION, RA,NUM, TYPE)VALUES (%s,%s,%s,%s,%s)
                            ''', [content_id,question,ra,mark,'short'])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))
def edit_question(request,course_id,topic_id,content_id,q_id):
    if request.method=='POST':
        with connections['eschool_db'].cursor() as c:
            c.execute('''SELECT TYPE FROM "Questions" WHERE Q_ID = %s
                        ''', [q_id])
            en = dictfetchone(c)
            if en["TYPE"] == "mcq":
                question = request.POST["question"]
                op1 = request.POST["op1"]
                op2 = request.POST["op2"]
                op3 = request.POST["op3"]
                op4 = request.POST["op4"]
                ra = request.POST["ra"]
                mark = request.POST["mark"]
                c.execute('''UPDATE "Questions" SET "QUESTION" = %s,OP1 = %s,OP2 = %s,OP3 = %s,OP4 = %s,RA = %s,NUM = %s WHERE Q_ID = %s
                            ''', [question,op1,op2,op3,op4,ra,mark,q_id])
            else:
                question = request.POST["question"]
                ra = request.POST["ra"]
                mark = request.POST["mark"]
                c.execute('''UPDATE "Questions" SET "QUESTION" = %s,RA = %s,NUM = %s WHERE Q_ID = %s
                            ''', [question,ra,mark,q_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))

def delete_question(request,course_id,topic_id,content_id,q_id):
    with connections['eschool_db'].cursor() as c:
        c.execute('''DELETE FROM "Questions" WHERE Q_ID = %s
                        ''', [q_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))
def up_question(request,course_id,topic_id,content_id,q_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('UP',[q_id,content_id,'Q'])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))
def down_question(request,course_id,topic_id,content_id,q_id):
    with connections['eschool_db'].cursor() as c:
        c.callproc('DOWN',[q_id,content_id,'Q'])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))

def give_exam(request,course_id,topic_id,content_id):
    print(request.POST)
    with connections['eschool_db'].cursor() as c:
        c.execute('''SELECT Q_ID,RA,NUM FROM
                        "Questions"
                        WHERE E_ID = %s
                        ORDER BY SERIAL
                        ''', [content_id])
        questions = dictfetchall(c)
        mark = 0
        for question in questions:
            temp = str(question["Q_ID"])
            if request.POST[temp] == question["RA"]:
                mark = mark + question["NUM"]
        c.execute('''SELECT COUNT(S_ID) CN FROM "Take_Exams" WHERE S_ID = %s AND E_ID = %s
                        ''', [request.session["userid"],content_id])
        en = dictfetchone(c)
        if en["CN"]==0:
            c.execute('''INSERT INTO "Take_Exams"(S_ID, E_ID, OBTAINED_MARKS) VALUES (%s,%s,%s)
                        ''', [request.session["userid"],content_id,mark])
        else:
            c.execute('''SELECT OBTAINED_MARKS FROM "Take_Exams" WHERE S_ID = %s AND E_ID = %s
                        ''', [request.session["userid"],content_id])
            en = dictfetchone(c)
            pmark = en["OBTAINED_MARKS"]
            if mark>pmark:
                c.execute('''UPDATE "Take_Exams" SET OBTAINED_MARKS = %s WHERE S_ID = %s AND E_ID = %s
                        ''', [mark,request.session["userid"],content_id])
    return redirect('/course/'+str(course_id)+'/topic/'+str(topic_id)+'/content/'+str(content_id))

def add_review(request,course_id):
    if request.method=='POST':
        ratting = request.POST["ratting"]
        review = request.POST["review"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''INSERT INTO "Feedback"(S_ID, C_ID, RATTING, REVIEW) VALUES (%s,%s,%s,%s)
                        ''', [request.session["userid"],course_id,ratting,review])
            c.callproc("UPDATE_RATTING",[course_id])
    return redirect('/course/'+str(course_id)+'')
def edit_review(request,course_id):
    if request.method=='POST':
        ratting = request.POST["ratting"]
        review = request.POST["review"]
        with connections['eschool_db'].cursor() as c:
            c.execute('''UPDATE "Feedback" SET RATTING = %s, REVIEW = %s WHERE S_ID = %s AND C_ID = %s
                        ''', [ratting,review,request.session["userid"],course_id])
            c.callproc("UPDATE_RATTING",[course_id])
    return redirect('/course/'+str(course_id)+'')
def delete_review(request,course_id):
    print("Delete_review",request.session["userid"],course_id)
    with connections['eschool_db'].cursor() as c:
        c.execute('''DELETE FROM "Feedback" WHERE S_ID = %s AND C_ID = %s
                    ''', [request.session["userid"],course_id])
        c.callproc("UPDATE_RATTING",[course_id])
    return redirect('/course/'+str(course_id)+'')