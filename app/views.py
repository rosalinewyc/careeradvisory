import json
from django.shortcuts import render
from django.shortcuts import HttpResponse
from app.models import *
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')


def login(request):
    return render(request, 'login.html', {})


def adminbootstrap(request):
    return render(request, 'adminbootstrap.html', {})


def courseplanner(request):
    return render(request, 'courseplanner.html', {})


def recommendjob(request):
    return render(request, 'recommendjob.html', {})


def modulesearch(request):
    return render(request, 'modulesearch.html', {})


def userprofile(request):
    return render(request, 'userprofile.html', {})


def authenticate(request):
    response = {}
    if request.method == 'POST':
        username_input = request.POST['username']
        password_input = request.POST['password']

        try:
            user = User.objects.get(user_id=username_input)
            if password_input == user.password:
                request.session['user'] = user.user_id
                request.session['role'] = user.role
                response['status'] = 'success'
            else:
                response['status'] = 'fail'
                response['message'] = 'Incorrect username and/or password!'
        except User.DoesNotExist:
            response['status'] = 'fail'
            response['message'] = 'No such user!'

        #print("Debug 1:" + str(username_input))
        #print("Debug 2:" + str(password_input))

    return HttpResponse(json.dumps(response), content_type="application/json")


def logout(request):
    response = {}
    if request.method == 'POST':
        del request.session['user']
        del request.session['role']

    session_user = request.session.get('user', None)
    session_role = request.session.get('role', None)

    if session_user is None and session_role is None:
        response['status'] = 'success'
    else:
        response['status'] = 'fail'
        response['message'] = 'Sign Out failed. Please try again.'

    return HttpResponse(json.dumps(response), content_type="application/json")
