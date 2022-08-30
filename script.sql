create sequence SEQ
/

create table "Users"
(
    USER_ID  NUMBER default ESCHOOL.SEQ.nextval not null
        constraint USERS_PK
            primary key,
    NAME     VARCHAR2(50)                       not null,
    EMAIL    VARCHAR2(50)                       not null,
    PASSWORD VARCHAR2(1000)                     not null,
    RDATE    DATE   default sysdate
)
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
    COURSE_ENROLLED NUMBER default 0 not null
)
/

create table "Teachers"
(
    T_ID         NUMBER       not null
        constraint TEACHERS_PK
            primary key
        constraint TEACHERS_USERS_USER_ID_FK
            references "Users",
    DESIGNATION  VARCHAR2(50) not null,
    COURSE_TAKEN NUMBER default 0
)
/

create table "Courses"
(
    COURSE_ID       NUMBER       default ESCHOOL.SEQ.nextval not null
        constraint COURSES_PK
            primary key,
    T_ID            NUMBER                                   not null
        constraint COURSES_TEACHERS_T_ID_FK
            references "Teachers",
    TITLE           VARCHAR2(100)                            not null,
    DESCRIPTIONS    VARCHAR2(1000),
    APPROVED        NUMBER       default 0                   not null,
    NUM_OF_STUDENTS NUMBER       default 0                   not null,
    RATTING         VARCHAR2(10) default '0'                 not null
)
/

create unique index COURSES_TITLE_UINDEX
    on "Courses" (TITLE)
/

create table "Enrollment"
(
    ENROLL_ID  NUMBER       default ESCHOOL.SEQ.nextval not null
        constraint ENROLLMENT_PK
            primary key,
    S_ID       NUMBER                                   not null
        constraint ENROLLMENT_STUDENTS_S_ID_FK
            references "Students",
    COURSE_ID  NUMBER                                   not null
        constraint ENROLLMENT_COURSES_COURSE_ID_FK
            references "Courses",
    "Date"     DATE         default CURRENT_DATE,
    ISAPPROVED NUMBER       default 0                   not null,
    PROGRESS   VARCHAR2(10) default '0',
    AVG_MARK   VARCHAR2(10) default 0
)
/

create unique index ENROLLMENT_COURSE_ID_S_ID_UINDEX
    on "Enrollment" (COURSE_ID, S_ID)
/

create trigger DELETE_ENROLLMENT
    before delete
    on "Enrollment"
    for each row
DECLARE

BEGIN
    IF :OLD.ISAPPROVED=1 THEN
        UPDATE "Students"
        SET COURSE_ENROLLED = COURSE_ENROLLED-1
        WHERE S_ID = :OLD.S_ID;

        UPDATE "Courses"
        SET NUM_OF_STUDENTS = NUM_OF_STUDENTS-1
        WHERE COURSE_ID = :OLD.COURSE_ID;
    END IF;

end;
/

create trigger ENROLLMENT_CONTROL
    before insert
    on "Enrollment"
    for each row
DECLARE
    C NUMBER;
    COURSED_APPROVAL_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( COURSED_APPROVAL_ERROR, -156  );
BEGIN
    SELECT COUNT(*) INTO C FROM "Courses" C1 WHERE C1.COURSE_ID= :NEW.COURSE_ID AND C1.APPROVED=0;
    IF C>0 THEN
        RAISE_APPLICATION_ERROR(-156, 'Course did not approved yet');
    end if;
end;
/

create table "Topics"
(
    TOPIC_ID           NUMBER default ESCHOOL.SEQ.nextval not null
        constraint TOPICS_PK
            primary key,
    TOPIC_NAME         VARCHAR2(100)                      not null,
    TOPIC_DESCRIPTIONS VARCHAR2(1000),
    COURSE_ID          NUMBER                             not null
        constraint TOPICS_COURSES_COURSE_ID_FK
            references "Courses",
    SERIAL             NUMBER default ESCHOOL.SEQ.nextval not null
)
/

create trigger TOPIC_CONTROL
    before insert
    on "Topics"
    for each row
DECLARE
    C NUMBER;
    COURSED_APPROVAL_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( COURSED_APPROVAL_ERROR, -156  );
BEGIN
    SELECT COUNT(*) INTO C FROM "Courses" C1 WHERE C1.COURSE_ID= :NEW.COURSE_ID AND C1.APPROVED=0;
    IF C>0 THEN
        RAISE_APPLICATION_ERROR(-156, 'Course did not approved yet');
    end if;
end;
/

create table "Contents"
(
    CONTENT_ID NUMBER default ESCHOOL.SEQ.nextval not null
        constraint CONTENTS_PK
            primary key,
    NAME       VARCHAR2(100)                      not null,
    TOPIC_ID   NUMBER                             not null
        constraint CONTENTS_TOPICS_TOPIC_ID_FK
            references "Topics",
    SERIAL     NUMBER default ESCHOOL.SEQ.nextval not null,
    TYPE       VARCHAR2(500)
)
/

create table "Lecture"
(
    L_ID        NUMBER not null
        constraint LECTURE_PK
            primary key
        constraint LECTURE_CONTENTS_CONTENT_ID_FK
            references "Contents",
    DESCRIPTION VARCHAR2(2000),
    VIDEO_LINK  VARCHAR2(200),
    DURATION    NUMBER
)
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

create table "Questions"
(
    Q_ID     NUMBER default ESCHOOL.SEQ.nextval not null
        constraint QUESTIONS_PK
            primary key,
    E_ID     NUMBER                             not null
        constraint QUESTIONS_QUIZS_E_ID_FK
            references "Quizs",
    QUESTION VARCHAR2(300)                      not null,
    OP1      VARCHAR2(100),
    OP2      VARCHAR2(100),
    OP3      VARCHAR2(100),
    OP4      VARCHAR2(100),
    RA       VARCHAR2(200)                      not null,
    NUM      NUMBER default 1                   not null,
    SERIAL   NUMBER default ESCHOOL.SEQ.nextval not null,
    TYPE     VARCHAR2(50)                       not null
)
/

create table "Take_Exams"
(
    ID             NUMBER default ESCHOOL.SEQ.nextval not null
        constraint TAKE_EXAMS_PK
            primary key,
    S_ID           NUMBER                             not null
        constraint TAKE_EXAMS_STUDENTS_S_ID_FK
            references "Students"
                on delete cascade,
    E_ID           NUMBER                             not null
        constraint TAKE_EXAMS_QUIZS_E_ID_FK
            references "Quizs"
                on delete cascade,
    OBTAINED_MARKS NUMBER                             not null,
    C_ID           NUMBER,
    STATUS         NUMBER default 0
)
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

    DELETE 
    FROM "Take_Exams"
    WHERE "Take_Exams".E_ID = :NEW.E_ID;
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
    DELETE 
    FROM "Take_Exams"
    WHERE "Take_Exams".E_ID = :OLD.E_ID;
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

    DELETE
    FROM "Take_Exams"
    WHERE "Take_Exams".E_ID = :NEW.E_ID;
end;
/

create trigger EXAM_CONTROL
    before insert
    on "Take_Exams"
    for each row
DECLARE
    T NUMBER;
    C NUMBER;
    C3 NUMBER;
    C4 NUMBER;
    STUDENT_ENROLLMENT_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( STUDENT_ENROLLMENT_ERROR, -150  );
BEGIN
    SELECT TOPIC_ID INTO T FROM "Contents" WHERE CONTENT_ID = :NEW.E_ID;

    SELECT COURSE_ID INTO C FROM "Topics" WHERE TOPIC_ID = T;

    SELECT COUNT(*) INTO C3 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND C = E.COURSE_ID AND E.ISAPPROVED=0;
    SELECT COUNT(*) INTO C4 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND C = E.COURSE_ID;
    IF C3>0 OR C4<1 THEN
        RAISE_APPLICATION_ERROR(-150, 'Student did not enrolled yet');
    end if;
end;
/

create trigger FIND_COURSE_ID
    before insert
    on "Take_Exams"
    for each row
DECLARE
    CID NUMBER;
    TID NUMBER;
BEGIN
    SELECT TOPIC_ID INTO TID FROM "Contents" WHERE CONTENT_ID = :NEW.E_ID;

    SELECT COURSE_ID INTO CID FROM "Topics" WHERE TOPIC_ID = TID;

    :NEW.C_ID := CID;

end;
/

create table "Forums"
(
    F_ID        NUMBER       default ESCHOOL.SEQ.nextval not null
        constraint FORUMS_PK
            primary key,
    C_ID        NUMBER                                   not null
        constraint FORUMS_COURSES_COURSE_ID_FK
            references "Courses",
    U_ID        NUMBER                                   not null
        constraint FORUMS_USERS_USER_ID_FK
            references "Users",
    PAR_COM_ID  NUMBER       default null
        constraint FORUMS_FORUMS_F_ID_FK
            references "Forums",
    DESCRIPTION VARCHAR2(1000)                           not null,
    "DATE"      TIMESTAMP(6) default CURRENT_TIMESTAMP,
    CHILD       NUMBER       default 0
)
/

create trigger FORUM_CONTROL
    before insert
    on "Forums"
    for each row
DECLARE
    C NUMBER;
    COURSED_APPROVAL_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( COURSED_APPROVAL_ERROR, -156  );

    C3 NUMBER;
    C4 NUMBER;
    STUDENT_ENROLLMENT_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( STUDENT_ENROLLMENT_ERROR, -150  );
    
    T1 NUMBER;
    T2 NUMBER;
    C5 NUMBER;
BEGIN
    SELECT COUNT(*) INTO C FROM "Courses" C1 WHERE C1.COURSE_ID= :NEW.C_ID AND C1.APPROVED=0;
    IF C>0 THEN
        RAISE_APPLICATION_ERROR(-156, 'Course did not approved yet');
    end if;
    
    SELECT COUNT(*) INTO C5 FROM "Teachers" WHERE T_ID = :NEW.U_ID;
    IF C5>0 THEN
        SELECT T_ID INTO T1  FROM "Teachers" WHERE T_ID = :NEW.U_ID;
        SELECT T_ID INTO T2  FROM "Courses" WHERE COURSE_ID = :NEW.C_ID;
        IF T1 != T2 THEN
            SELECT COUNT(*) INTO C3 FROM "Enrollment" E WHERE :NEW.U_ID = E.S_ID AND :NEW.C_ID = E.COURSE_ID AND E.ISAPPROVED=0;
            SELECT COUNT(*) INTO C4 FROM "Enrollment" E WHERE :NEW.U_ID = E.S_ID AND :NEW.C_ID = E.COURSE_ID;
            IF C3>0 OR C4<1 THEN
                RAISE_APPLICATION_ERROR(-150, 'Student did not enrolled yet');
            end if;
        end if;
    end if;
end;
/

create table "Notifications"
(
    ID     NUMBER       default ESCHOOL.SEQ.nextval not null
        constraint NOTIFICATIONS_PK
            primary key,
    U_ID   NUMBER
        constraint NOTIFICATIONS_USERS_USER_ID_FK
            references "Users"
                on delete cascade,
    SEEN   NUMBER       default 0                   not null,
    "DATE" TIMESTAMP(6) default CURRENT_TIMESTAMP   not null,
    KEY    NUMBER       default null,
    "FOR"  VARCHAR2(50)
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
    FDATE   TIMESTAMP(6) default SYSTIMESTAMP,
    constraint FEEDBACK_PK
        primary key (S_ID, C_ID)
)
/

create trigger FEEDBACK_CONTROL
    before insert
    on "Feedback"
    for each row
DECLARE
    C NUMBER;
    COURSED_APPROVAL_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( COURSED_APPROVAL_ERROR, -156  );

    C3 NUMBER;
    C4 NUMBER;
    STUDENT_ENROLLMENT_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( STUDENT_ENROLLMENT_ERROR, -150  );
BEGIN
    SELECT COUNT(*) INTO C FROM "Courses" C1 WHERE C1.COURSE_ID= :NEW.C_ID AND C1.APPROVED=0;
    IF C>0 THEN
        RAISE_APPLICATION_ERROR(-156, 'Course did not approved yet');
    end if;

    SELECT COUNT(*) INTO C3 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND :NEW.C_ID = E.COURSE_ID AND E.ISAPPROVED=0;
    SELECT COUNT(*) INTO C4 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND :NEW.C_ID = E.COURSE_ID;
    IF C3>0 OR C4<1 THEN
        RAISE_APPLICATION_ERROR(-150, 'Student did not enrolled yet');
    end if;
end;
/

create table "Completion"
(
    S_ID NUMBER not null
        constraint COMPLETION_STUDENTS_S_ID_FK
            references "Students"
                on delete cascade,
    L_ID NUMBER not null
        constraint COMPLETION_LECTURE_L_ID_FK
            references "Lecture"
                on delete cascade,
    constraint COMPLETION_PK
        primary key (S_ID, L_ID)
)
/

create trigger COMPLETION_CONTROL
    before insert
    on "Completion"
    for each row
DECLARE
    T NUMBER;
    C NUMBER;
    C3 NUMBER;
    C4 NUMBER;
    STUDENT_ENROLLMENT_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( STUDENT_ENROLLMENT_ERROR, -150  );
BEGIN
    SELECT TOPIC_ID INTO T FROM "Contents" WHERE CONTENT_ID = :NEW.L_ID;

    SELECT COURSE_ID INTO C FROM "Topics" WHERE TOPIC_ID = T;

    SELECT COUNT(*) INTO C3 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND C = E.COURSE_ID AND E.ISAPPROVED=0;
    SELECT COUNT(*) INTO C4 FROM "Enrollment" E WHERE :NEW.S_ID = E.S_ID AND C = E.COURSE_ID;
    IF C3>0 OR C4<1 THEN
        RAISE_APPLICATION_ERROR(-150, 'Student did not enrolled yet');
    end if;
end;
/

create table "Contribute"
(
    T_ID NUMBER not null
        constraint CONTRIBUTE_TEACHERS_T_ID_FK
            references "Teachers",
    C_ID NUMBER not null
        constraint CONTRIBUTE_COURSES_COURSE_ID_FK
            references "Courses",
    constraint CONTRIBUTE_PK
        primary key (T_ID, C_ID)
)
/

create trigger CONTRIBUTE_CONTROL
    before insert
    on "Contribute"
    for each row
DECLARE
    C NUMBER;
    COURSED_APPROVAL_ERROR EXCEPTION ;
    PRAGMA EXCEPTION_INIT ( COURSED_APPROVAL_ERROR, -156  );
BEGIN
    SELECT COUNT(*) INTO C FROM "Courses" C1 WHERE C1.COURSE_ID= :NEW.C_ID AND C1.APPROVED=0;
    IF C>0 THEN
        RAISE_APPLICATION_ERROR(-156, 'Course did not approved yet');
    end if;
end;
/

create trigger CONTRIBUTE_INSERTION
    after insert
    on "Contribute"
    for each row
DECLARE

BEGIN
    UPDATE "Teachers" S
    SET S.COURSE_TAKEN = S.COURSE_TAKEN + 1
    WHERE S.T_ID = :NEW.T_ID;

end;
/

create trigger DELETE_CONTRIBUTE
    before delete
    on "Contribute"
    for each row
DECLARE

BEGIN
    UPDATE "Teachers" S
    SET S.COURSE_TAKEN = S.COURSE_TAKEN - 1
    WHERE S.T_ID = :OLD.T_ID;

end;
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
    FROM "Lecture" Q
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

create PROCEDURE DELETE_COURSE(CID IN NUMBER) IS
    CURSOR C1 IS SELECT * FROM "Forums" WHERE C_ID = CID;
    CURSOR C2 IS SELECT * FROM "Topics" WHERE COURSE_ID = CID;
    F NUMBER;
BEGIN
    SELECT APPROVED INTO F FROM "Courses" WHERE COURSE_ID = CID;
    IF F=1 THEN 
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
        WHERE C_ID = CID;
    
        DELETE
        FROM "Enrollment"
        WHERE COURSE_ID = CID;
    
        DELETE
        FROM "Contribute"
        WHERE C_ID= CID;
    
        UPDATE "Teachers" T
        SET T.COURSE_TAKEN = T.COURSE_TAKEN -1
        WHERE T.T_ID = (SELECT T_ID
                        FROM "Courses"
                        WHERE COURSE_ID = CID);
    
        DELETE
        FROM "Notifications" N
        WHERE N.ID IN (SELECT N2.ID FROM "Notifications" N2 WHERE N2.KEY = CID);
    
        DELETE
        FROM "Courses"
        WHERE COURSE_ID = CID;
    ElSE
        DELETE
        FROM "Courses"
        WHERE COURSE_ID = CID;
    END IF;
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
    FROM "Contribute"
    WHERE T_ID = ID;

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
    FROM "Notifications"
    WHERE U_ID = ID;
    
    DELETE
    FROM "Users"
    WHERE USER_ID = ID;
end;
/

create PROCEDURE APPROVED_COURSE(ID IN NUMBER) IS
  TID NUMBER;
  IS_APRV NUMBER;
BEGIN
    SELECT T_ID,APPROVED INTO TID,IS_APRV FROM "Courses" WHERE COURSE_ID = ID;
    IF IS_APRV=0 THEN
        UPDATE "Teachers" T
        SET T.COURSE_TAKEN = T.COURSE_TAKEN + 1
        WHERE T.T_ID = TID;

        UPDATE "Courses"
        SET APPROVED = 1
        WHERE COURSE_ID = ID;

        INSERT INTO "Forums"(C_ID, U_ID, DESCRIPTION) VALUES (ID,TID,'DISCUSS YOUR PROBLEMS HERE');
    end if;

    
end;
/

create PROCEDURE REEJECTED_COURSE(ID IN NUMBER) IS
 
BEGIN
    UPDATE "Courses"
    SET APPROVED = -1
    WHERE COURSE_ID = ID;
end;
/

create PROCEDURE REEJECTED_STUDENT(SID IN NUMBER,C_ID IN NUMBER) IS

BEGIN
    UPDATE "Enrollment"
    SET ISAPPROVED = -1
    WHERE COURSE_ID = C_ID AND S_ID = SID;
end;
/

create PROCEDURE APPROVED_STUDENT(SID IN NUMBER,C_ID IN NUMBER) IS
    IS_APRV NUMBER;

BEGIN
    SELECT ISAPPROVED INTO IS_APRV FROM "Enrollment" WHERE S_ID = SID AND COURSE_ID = C_ID;
    IF IS_APRV=0 THEN
        UPDATE "Students" S
        SET S.COURSE_ENROLLED = S.COURSE_ENROLLED + 1
        WHERE S.S_ID = SID;

        UPDATE "Courses" C
        SET C.NUM_OF_STUDENTS = C.NUM_OF_STUDENTS + 1
        WHERE C.COURSE_ID = C_ID;

        UPDATE "Enrollment"
        SET ISAPPROVED = 1
        WHERE S_ID = SID AND COURSE_ID = C_ID;
    end if;
end;
/

create FUNCTION DO_LOGIN(MAIL IN VARCHAR2, UID OUT NUMBER)
    RETURN VARCHAR2 AS
    C1 NUMBER;
    C2 NUMBER;
BEGIN
    SELECT USER_ID INTO UID FROM "Users" WHERE EMAIL = MAIL;
    SELECT COUNT(*) INTO C1 FROM "Students" WHERE S_ID = UID;
    SELECT COUNT(*) INTO C2 FROM "Teachers" WHERE T_ID = UID;
    IF C1 > 0 THEN
        RETURN 'student';
    ELSE
        IF C2 > 0 THEN
            RETURN 'teacher';
        ELSE
            RETURN 'admin';
        end if;
    end if;
end;
/

create FUNCTION REGISTER_STUDENT(NAM IN VARCHAR2, MAIL IN VARCHAR2, PASS IN VARCHAR2,  SID OUT NUMBER)
    RETURN VARCHAR2 AS

    C NUMBER;

BEGIN
    SELECT COUNT(*) INTO C FROM "Users" WHERE EMAIL = MAIL ;
    IF C>0 THEN
        SID := -1;
        RETURN 'Email already exist';
    ELSE
        INSERT INTO "Users"(name, email, password) values(NAM, MAIL,PASS);
        SELECT USER_ID INTO SID FROM "Users" WHERE MAIL = EMAIL;
        INSERT INTO "Students"(S_ID) VALUES (SID);
        RETURN 'Successfull';
    end if;
end;
/

create FUNCTION REGISTER_TEACHER(NAM IN VARCHAR2, MAIL IN VARCHAR2, PASS IN VARCHAR2,  DESIG IN VARCHAR2 ,TID OUT NUMBER)
    RETURN VARCHAR2 AS

    C NUMBER;

BEGIN
    SELECT COUNT(*) INTO C FROM "Users" WHERE EMAIL = MAIL ;
    IF C>0 THEN
        TID := -1;
        RETURN 'Email already exist';
    ELSE
        INSERT INTO "Users"(name, email, password) values(NAM, MAIL,PASS);
        SELECT USER_ID INTO TID FROM "Users" WHERE MAIL = EMAIL;
        INSERT INTO "Teachers"(T_ID, DESIGNATION) VALUES (TID,DESIG);
        RETURN 'Successfull';
    end if;
end;
/

create FUNCTION CHECK_USER(UID IN NUMBER)
    RETURN VARCHAR2 AS

    C NUMBER;
    C1 NUMBER;
    C2 NUMBER;
BEGIN
    SELECT COUNT(*) INTO C FROM "Users" WHERE USER_ID = UID;
    IF C>0 THEN
        SELECT COUNT(*) INTO C1 FROM "Students" WHERE S_ID = UID;
        SELECT COUNT(*) INTO C2 FROM "Teachers" WHERE T_ID = UID;
        IF C1 > 0 THEN
            RETURN 'student';
        ELSE
            IF C2 > 0 THEN
                RETURN 'teacher';
            ELSE
                RETURN 'admin';
            end if;
        end if;
    ELSE
        RETURN 'Invalid User';
    end if;
end;
/

create PROCEDURE UPDATE_PROGRESS(SID IN NUMBER, CID IN NUMBER) IS
    NC NUMBER;
    NL NUMBER;
    NE NUMBER;
    MRK NUMBER;
    TMRK VARCHAR2(15);
    OMRK VARCHAR2(15);
    CURSOR DATA IS SELECT * FROM "Take_Exams" WHERE S_ID = SID AND E_ID IN (SELECT CONTENT_ID  FROM "Contents" WHERE TOPIC_ID IN ( SELECT TOPIC_ID FROM "Topics" WHERE COURSE_ID = CID ));
BEGIN
    SELECT COUNT(CONTENT_ID) INTO NC FROM "Contents" WHERE TOPIC_ID IN (
        SELECT TOPIC_ID FROM "Topics" WHERE COURSE_ID = CID
        );
    SELECT COUNT(L_ID) INTO NL FROM "Completion" WHERE S_ID = SID AND
    L_ID IN (SELECT CONTENT_ID  FROM "Contents" WHERE TOPIC_ID IN (
        SELECT TOPIC_ID FROM "Topics" WHERE COURSE_ID = CID
        ));
    NE := 0;
    TMRK := 0;
    OMRK := 0;

     FOR E IN DATA
        LOOP
            SELECT MARKS INTO MRK FROM "Quizs" WHERE E_ID = E.E_ID;
            OMRK := OMRK + E.OBTAINED_MARKS;
            TMRK := TMRK + MRK;
            IF E.OBTAINED_MARKS*2>=MRK THEN
                NE := NE+1;
            end if;
    end loop;

    if NC>0 THEN
        UPDATE "Enrollment"
        SET PROGRESS = round(((NE+NL)/NC)*100,2)
        WHERE S_ID = SID AND COURSE_ID = CID;
    end if;

    if TMRK>0 then
        UPDATE "Enrollment"
        SET AVG_MARK = ROUND((OMRK/TMRK)*100,2)
        WHERE S_ID = SID AND COURSE_ID = CID;
    end if;
end;
/

create PROCEDURE UP(ID IN NUMBER, FID IN NUMBER, F IN VARCHAR2) AS
    S1 NUMBER;
    S2 NUMBER;
    ID2 NUMBER;
    CNT NUMBER;

BEGIN
    IF F = 'T' THEN
        SELECT SERIAL INTO S1 FROM "Topics" WHERE TOPIC_ID = ID;
        SELECT COUNT(TOPIC_ID) INTO  CNT FROM "Topics" WHERE COURSE_ID = FID AND SERIAL<S1;
        IF CNT>0 THEN
            SELECT MAX(SERIAL) INTO S2 FROM "Topics" WHERE COURSE_ID = FID AND SERIAL<S1;
            SELECT TOPIC_ID INTO ID2 FROM "Topics" WHERE COURSE_ID = FID AND SERIAL = S2;
            UPDATE "Topics" SET SERIAL = S1 WHERE TOPIC_ID = ID2;
            UPDATE "Topics" SET SERIAL = S2 WHERE TOPIC_ID = ID;
        end if;
    ELSIF F = 'C' THEN
        SELECT SERIAL INTO S1 FROM "Contents" WHERE CONTENT_ID = ID;
        SELECT COUNT(CONTENT_ID) INTO  CNT FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL<S1;
        IF CNT>0 THEN
            SELECT MAX(SERIAL) INTO S2 FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL<S1;
            SELECT CONTENT_ID INTO ID2 FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL = S2;
            UPDATE "Contents" SET SERIAL = S1 WHERE CONTENT_ID = ID2;
            UPDATE "Contents" SET SERIAL = S2 WHERE CONTENT_ID = ID;
        end if;
    ELSE
        SELECT SERIAL INTO S1 FROM "Questions" WHERE Q_ID = ID;
        SELECT COUNT(Q_ID) INTO  CNT FROM "Questions" WHERE E_ID = FID AND SERIAL<S1;
        IF CNT>0 THEN
            SELECT MAX(SERIAL) INTO S2 FROM "Questions" WHERE E_ID = FID AND SERIAL<S1;
            SELECT Q_ID INTO ID2 FROM "Questions" WHERE E_ID = FID AND SERIAL = S2;
            UPDATE "Questions" SET SERIAL = S1 WHERE Q_ID = ID2;
            UPDATE "Questions" SET SERIAL = S2 WHERE Q_ID = ID;
        end if;
    end if;
end;
/

create PROCEDURE DOWN(ID IN NUMBER, FID IN NUMBER, F IN VARCHAR2) AS
    S1 NUMBER;
    S2 NUMBER;
    ID2 NUMBER;
    CNT NUMBER;

BEGIN
    IF F = 'T' THEN
        SELECT SERIAL INTO S1 FROM "Topics" WHERE TOPIC_ID = ID;
        SELECT COUNT(TOPIC_ID) INTO  CNT FROM "Topics" WHERE COURSE_ID = FID AND SERIAL>S1;
        IF CNT>0 THEN
            SELECT MIN(SERIAL) INTO S2 FROM "Topics" WHERE COURSE_ID = FID AND SERIAL>S1;
            SELECT TOPIC_ID INTO ID2 FROM "Topics" WHERE COURSE_ID = FID AND SERIAL = S2;
            UPDATE "Topics" SET SERIAL = S1 WHERE TOPIC_ID = ID2;
            UPDATE "Topics" SET SERIAL = S2 WHERE TOPIC_ID = ID;
        end if;
    ELSIF F = 'C' THEN
        SELECT SERIAL INTO S1 FROM "Contents" WHERE CONTENT_ID = ID;
        SELECT COUNT(CONTENT_ID) INTO  CNT FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL>S1;
        IF CNT>0 THEN
            SELECT MIN(SERIAL) INTO S2 FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL>S1;
            SELECT CONTENT_ID INTO ID2 FROM "Contents" WHERE TOPIC_ID = FID AND SERIAL = S2;
            UPDATE "Contents" SET SERIAL = S1 WHERE CONTENT_ID = ID2;
            UPDATE "Contents" SET SERIAL = S2 WHERE CONTENT_ID = ID;
        end if;
    ELSE
        SELECT SERIAL INTO S1 FROM "Questions" WHERE Q_ID = ID;
        SELECT COUNT(Q_ID) INTO  CNT FROM "Questions" WHERE E_ID = FID AND SERIAL>S1;
        IF CNT>0 THEN
            SELECT MIN(SERIAL) INTO S2 FROM "Questions" WHERE E_ID = FID AND SERIAL>S1;
            SELECT Q_ID INTO ID2 FROM "Questions" WHERE E_ID = FID AND SERIAL = S2;
            UPDATE "Questions" SET SERIAL = S1 WHERE Q_ID = ID2;
            UPDATE "Questions" SET SERIAL = S2 WHERE Q_ID = ID;
        end if;
    end if;
end;
/

create PROCEDURE NOTIFY_STUDENTS(CID IN NUMBER) IS
CURSOR C1 IS SELECT S_ID FROM "Enrollment" WHERE COURSE_ID = CID;
CNT NUMBER;
BEGIN
    FOR C IN C1
    LOOP
        SELECT COUNT(ID) INTO CNT FROM "Notifications" WHERE U_ID = C.S_ID AND KEY = CID AND "FOR" = 'post';
        IF CNT = 0 THEN
            INSERT INTO "Notifications"(U_ID, "FOR",KEY) VALUES (C.S_ID,'post',CID);
        ELSE
            UPDATE "Notifications" SET SEEN = 0 WHERE U_ID = C.S_ID AND KEY = CID AND "FOR" = 'post';
        end if;

    end loop;
end;
/


