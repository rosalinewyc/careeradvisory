from django.shortcuts import render

def login(): # direct to login. html upon clicking logout
    return HttpResponseRedirect('login')