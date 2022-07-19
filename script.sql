create sequence SEQ
/

create table "Users"
(
    USER_ID     NUMBER default AHE.SEQ.nextval not null
        constraint USERS_PK
            primary key,
    NAME        VARCHAR2(50)                   not null,
    EMAIL       VARCHAR2(50)                   not null,
    PASSWORD    VARCHAR2(50)                   not null,
    MOBILE_NO   NUMBER,
    INSTITUTION VARCHAR2(50)
)
/

comment on table "Users" is 'ALL user''s table e.c Students, Teachers'
/

create unique index USERS_EMAIL_UINDEX
    on "Users" (EMAIL)
/

create table "Students"
(
    S_ID            NUMBER           not null
        constraint STUDENTS_PK
            primary key
        constraint STUDENTS_USERS_USER_ID_FK
            references "Users",
    CLASS           NUMBER,
    DEPT            VARCHAR2(50),
    COURSE_ENROLLED NUMBER default 0 not null
)
/

comment on table "Students" is 'Student''s table'
/

create table "Teachers"
(
    T_ID         NUMBER       not null
        constraint TEACHERS_PK
            primary key
        constraint TEACHERS_USERS_USER_ID_FK
            references "Users",
    SPECIALITY   VARCHAR2(50) not null,
    DESIGNATION  VARCHAR2(50) not null,
    COURSE_TAKEN NUMBER default 0
)
/

comment on table "Teachers" is 'Teacher''s Table'
/

create table "Courses"
(
    COURSE_ID       NUMBER       default AHE.SEQ.nextval not null
        constraint COURSES_PK
            primary key,
    T_ID            NUMBER                               not null
        constraint COURSES_TEACHERS_T_ID_FK
            references "Teachers",
    TITLE           VARCHAR2(100)                        not null,
    SUBJECT         VARCHAR2(50)                         not null,
    DESCRIPTIONS    VARCHAR2(200),
    "LEVEL"         VARCHAR2(100),
    APPROVED        NUMBER       default 0               not null,
    NUM_OF_STUDENTS NUMBER       default 0               not null,
    RATTING         VARCHAR2(10) default '0'             not null
)
/

comment on table "Courses" is 'Course''s Table'
/

create unique index COURSES_TITLE_UINDEX
    on "Courses" (TITLE)
/

create trigger COURSE_INSERTION
    after insert
    on "Courses"
    for each row
DECLARE

BEGIN
    UPDATE "Teachers" T
    SET T.COURSE_TAKEN = T.COURSE_TAKEN + 1
    WHERE T.T_ID = :NEW.T_ID;
    INSERT INTO "Forums"(C_ID, U_ID, DESCRIPTION) VALUES (:NEW.COURSE_ID,:NEW.T_ID,'DISCUSS YOUR PROBLEMS HERE');
end;
/

create table "Admins"
(
    ADMIN_ID NUMBER default AHE.SEQ.nextval not null
        constraint ADMINS_PK
            primary key,
    NAME     VARCHAR2(50)                   not null,
    EMAIL    VARCHAR2(50)                   not null,
    PASSWORD VARCHAR2(50)                   not null
)
/

comment on table "Admins" is 'Admin''s Table'
/

create unique index ADMINS_EMAIL_UINDEX
    on "Admins" (EMAIL)
/

create table "Enrollment"
(
    ENROLL_ID NUMBER default AHE.SEQ.nextval not null
        constraint ENROLLMENT_PK
            primary key,
    S_ID      NUMBER                         not null
        constraint ENROLLMENT_STUDENTS_S_ID_FK
            references "Students",
    COURSE_ID NUMBER                         not null
        constraint ENROLLMENT_COURSES_COURSE_ID_FK
            references "Courses",
    "Date"    DATE   default CURRENT_DATE
)
/

comment on table "Enrollment" is 'Courses enrollment history'
/

create unique index ENROLLMENT_COURSE_ID_S_ID_UINDEX
    on "Enrollment" (COURSE_ID, S_ID)
/

create trigger ENROLLMENT_INSERTION
    after insert
    on "Enrollment"
    for each row
DECLARE

BEGIN
    UPDATE "Students" S
    SET S.COURSE_ENROLLED = S.COURSE_ENROLLED + 1
    WHERE S.S_ID = :NEW.S_ID;

    UPDATE "Courses" C
    SET C.NUM_OF_STUDENTS = C.NUM_OF_STUDENTS + 1
    WHERE C.COURSE_ID = :NEW.COURSE_ID;

end;
/

create trigger DELETE_ENROLLMENT
    before delete
    on "Enrollment"
    for each row
DECLARE

BEGIN
    UPDATE "Students"
    SET COURSE_ENROLLED = COURSE_ENROLLED-1
    WHERE S_ID = :OLD.S_ID;

    UPDATE "Courses"
    SET NUM_OF_STUDENTS = NUM_OF_STUDENTS-1
    WHERE COURSE_ID = :OLD.COURSE_ID;

end;
/

create table "Topics"
(
    TOPIC_ID           NUMBER default AHE.SEQ.nextval not null
        constraint TOPICS_PK
            primary key,
    TOPIC_NAME         VARCHAR2(100)                  not null,
    TOPIC_DESCRIPTIONS VARCHAR2(250),
    COURSE_ID          NUMBER                         not null
        constraint TOPICS_COURSES_COURSE_ID_FK
            references "Courses",
    SERIAL             NUMBER default AHE.SEQ.nextval not null
)
/

comment on table "Topics" is 'Content''s topics of  courses'
/

create table "Contents"
(
    CONTENT_ID NUMBER default AHE.SEQ.nextval not null
        constraint CONTENTS_PK
            primary key,
    NAME       VARCHAR2(100)                  not null,
    TOPIC_ID   NUMBER                         not null
        constraint CONTENTS_TOPICS_TOPIC_ID_FK
            references "Topics",
    SERIAL     NUMBER default AHE.SEQ.nextval not null
)
/

comment on table "Contents" is 'Contents of courses'
/

create unique index CONTENTS_SERIAL_UINDEX
    on "Contents" (SERIAL)
/

create table "Video_Contents"
(
    L_ID        NUMBER        not null
        constraint VIDEO_CONTENTS_PK
            primary key
        constraint VIDEO_CONTENTS_CONTENTS_CONTENT_ID_FK
            references "Contents",
    LINK        VARCHAR2(100) not null,
    DESCRIPTION VARCHAR2(250),
    DURATION    NUMBER        not null
)
/

comment on table "Video_Contents" is 'Video_Lecture of courses'
/

create table "Quizs"
(
    E_ID             NUMBER           not null
        constraint QUIZS_PK
            primary key
        constraint QUIZS_CONTENTS_CONTENT_ID_FK
            references "Contents",
    MARKS            NUMBER default 0 not null,
    NUM_OF_QUESTIONS NUMBER default 0 not null
)
/

comment on table "Quizs" is 'Exam table'
/

create table "Questions"
(
    Q_ID        NUMBER default AHE.SEQ.nextval not null
        constraint QUESTIONS_PK
            primary key,
    E_ID        NUMBER                         not null
        constraint QUESTIONS_QUIZS_E_ID_FK
            references "Quizs",
    "Questions" VARCHAR2(150)                  not null,
    OP1         VARCHAR2(75)                   not null,
    OP2         VARCHAR2(75)                   not null,
    OP3         VARCHAR2(75)                   not null,
    OP4         VARCHAR2(75)                   not null,
    RA          NUMBER                         not null,
    NUM         NUMBER default 1               not null,
    SERIAL      NUMBER default AHE.SEQ.nextval
)
/

comment on table "Questions" is 'Question''s of quizes'
/

create trigger QUESTION_INSERTION
    after insert
    on "Questions"
    for each row
DECLARE

BEGIN
    update "Quizs" Q
    set  Q.MARKS = Q.MARKS + :NEW.NUM, Q.NUM_OF_QUESTIONS = Q.NUM_OF_QUESTIONS + 1
    WHERE Q.E_ID  = :NEW.E_ID;
end;
/

create trigger DELETE_QUESTION
    before delete
    on "Questions"
    for each row
DECLARE

BEGIN
    UPDATE "Quizs" Q
    SET Q.NUM_OF_QUESTIONS = Q.NUM_OF_QUESTIONS-1, Q.MARKS = Q.MARKS - :OLD.NUM
    WHERE Q.E_ID = :OLD.E_ID;
end;
/

create trigger UPDATE_QUESTION
    after update
    on "Questions"
    for each row
DECLARE

BEGIN
    update "Quizs" Q
    set  Q.MARKS = Q.MARKS + :NEW.NUM - :OLD.NUM
    WHERE Q.E_ID  = :NEW.E_ID;
end;
/

create table "Take_Exams"
(
    ID             NUMBER default AHE.SEQ.nextval not null
        constraint TAKE_EXAMS_PK
            primary key,
    S_ID           NUMBER                         not null
        constraint TAKE_EXAMS_STUDENTS_S_ID_FK
            references "Students"
                on delete cascade,
    E_ID           NUMBER                         not null
        constraint TAKE_EXAMS_QUIZS_E_ID_FK
            references "Quizs"
                on delete cascade,
    CORRECTED_QUES NUMBER                         not null,
    OBTAINED_MARKS NUMBER                         not null
)
/

comment on table "Take_Exams" is 'Exam''s history table'
/

create table "Forums"
(
    F_ID        NUMBER       default AHE.SEQ.nextval not null
        constraint FORUMS_PK
            primary key,
    C_ID        NUMBER                               not null
        constraint FORUMS_COURSES_COURSE_ID_FK
            references "Courses",
    U_ID        NUMBER                               not null
        constraint FORUMS_USERS_USER_ID_FK
            references "Users",
    PAR_COM_ID  NUMBER       default null
        constraint FORUMS_FORUMS_F_ID_FK
            references "Forums",
    DESCRIPTION VARCHAR2(250)                        not null,
    "DATE"      TIMESTAMP(6) default CURRENT_TIMESTAMP
)
/

comment on table "Forums" is 'Disscussion Forum''s table of courses'
/

create table "Notifications"
(
    ID     NUMBER       default AHE.SEQ.nextval   not null
        constraint NOTIFICATIONS_PK
            primary key,
    U_ID   NUMBER                                 not null
        constraint NOTIFICATIONS_USERS_USER_ID_FK
            references "Users"
                on delete cascade,
    SEEN   NUMBER       default 0                 not null,
    "DATE" TIMESTAMP(6) default CURRENT_TIMESTAMP not null,
    C_ID   NUMBER       default -1
)
/

create table DJANGO_MIGRATIONS
(
    ID      NUMBER(19) generated by default on null as identity
        primary key,
    APP     NVARCHAR2(255),
    NAME    NVARCHAR2(255),
    APPLIED TIMESTAMP(6) not null
)
/

create table "Feedback"
(
    S_ID    NUMBER                    not null
        constraint FEEDBACK_STUDENTS_S_ID_FK
            references "Students",
    C_ID    NUMBER                    not null
        constraint FEEDBACK_COURSES_COURSE_ID_FK
            references "Courses",
    RATTING VARCHAR2(10) default null not null,
    REVIEW  VARCHAR2(250),
    constraint FEEDBACK_PK
        primary key (S_ID, C_ID)
)
/

comment on table "Feedback" is 'Enrolled student''s feedback on courses'
/

create table "Completion"
(
    S_ID NUMBER not null
        constraint COMPLETION_STUDENTS_S_ID_FK
            references "Students"
                on delete cascade,
    L_ID NUMBER not null
        constraint COMPLETION_VIDEO_CONTENTS_L_ID_FK
            references "Video_Contents"
                on delete cascade,
    constraint COMPLETION_PK
        primary key (S_ID, L_ID)
)
/

create PROCEDURE DELETE_QUIZ(ID IN NUMBER) AS
BEGIN
    DELETE
    FROM "Questions" Q
    WHERE Q.E_ID = ID;

    DELETE
    FROM "Quizs" Q
    WHERE Q.E_ID = ID;
end;
/

create PROCEDURE DELETE_CONTENT(ID IN NUMBER) AS
BEGIN
    DELETE_QUIZ(ID);

    DELETE
    FROM "Video_Contents" Q
    WHERE Q.L_ID = ID;

    DELETE
    FROM "Contents" Q
    WHERE Q.CONTENT_ID = ID;


end;
/

create PROCEDURE DELETE_TOPIC(ID IN NUMBER) IS
    CURSOR DATA IS SELECT * FROM "Contents" WHERE TOPIC_ID = ID;
BEGIN
    FOR C IN DATA
    LOOP
        DELETE_CONTENT(C.CONTENT_ID);
    end loop;

    DELETE
    FROM "Topics" Q
    WHERE Q.TOPIC_ID = ID;


end;
/

create PROCEDURE DELETE_FORUM(ID IN NUMBER) IS

BEGIN
    DELETE
    FROM "Forums" Q
    WHERE Q.F_ID = ID OR Q.PAR_COM_ID=ID;
end;
/

create PROCEDURE UPDATE_RATTING(ID IN NUMBER) IS
    T VARCHAR2(50);
    N NUMBER;
BEGIN
    SELECT COUNT(RATTING), SUM(RATTING) INTO N,T
    FROM "Feedback"
    WHERE C_ID = ID;

    IF N>0 THEN
        UPDATE "Courses"
        SET RATTING = ROUND(T/N,2)
        WHERE COURSE_ID = ID;
    ELSE
        UPDATE "Courses"
        SET RATTING = 0
        WHERE COURSE_ID = ID;
    end if;
end;
/

create PROCEDURE DELETE_COURSE(ID IN NUMBER) IS
    CURSOR C1 IS SELECT * FROM "Forums" WHERE C_ID = ID;
    CURSOR C2 IS SELECT * FROM "Topics" WHERE COURSE_ID = ID;

BEGIN
    FOR C IN C1
    LOOP
        DELETE_FORUM(C.F_ID);
    end loop;

    FOR C IN C2
    LOOP
        DELETE_TOPIC(C.TOPIC_ID);
    end loop;

    DELETE
    FROM "Feedback"
    WHERE C_ID = ID;

    DELETE
    FROM "Enrollment"
    WHERE COURSE_ID = ID;

    UPDATE "Teachers" T
    SET T.COURSE_TAKEN = T.COURSE_TAKEN -1
    WHERE T.T_ID = (SELECT T_ID
                    FROM "Courses"
                    WHERE COURSE_ID = ID);

    DELETE
    FROM "Notifications" N
    WHERE N.C_ID = ID;

    DELETE
    FROM "Courses"
    WHERE COURSE_ID = ID;
end;
/

create PROCEDURE DELETE_STUDENT(ID IN NUMBER) IS
BEGIN

    DELETE
    FROM "Enrollment"
    WHERE S_ID = ID;

    DELETE
    FROM "Feedback"
    WHERE S_ID = ID;

    DELETE
    FROM "Students"
    WHERE S_ID = ID;
end;
/

create PROCEDURE DELETE_TEACHER(ID IN NUMBER) IS
    CURSOR C1 IS SELECT * FROM "Courses" WHERE T_ID = ID;
BEGIN
    FOR C IN C1
    LOOP
        DELETE_COURSE(C.COURSE_ID);
    end loop;

    DELETE
    FROM "Teachers"
    WHERE T_ID = ID;
end;
/

create PROCEDURE DELETE_USER(ID IN NUMBER) IS
    CURSOR C1 IS SELECT * FROM "Forums" WHERE U_ID = ID;
BEGIN
    DELETE_STUDENT(ID);
    DELETE_TEACHER(ID);
    FOR C IN C1
    LOOP
        DELETE_FORUM(C.F_ID);
    end loop;
    
    DELETE
    FROM "Users"
    WHERE USER_ID = ID;
end;
/


