from django.shortcuts import render

def login(request): # direct to login. html upon clicking logout
    return HttpResponseRedirect('login')