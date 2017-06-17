from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect

def login(request): # direct to login. html upon clicking logout
    return HttpResponseRedirect('login')