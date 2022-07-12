from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def profile(request,user_id):
    return HttpResponse("From Profile")