from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def profile(request,user_id):
    return render(request,'profile.html', {'num_of_not':5})


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






