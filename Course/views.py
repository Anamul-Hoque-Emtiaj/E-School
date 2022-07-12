from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def course_details(request,course_id):
    return HttpResponse("From course_details")