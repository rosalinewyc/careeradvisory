import json
import csv
import io
from zipfile import *
from django.core import serializers
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators import csrf
from app.models import *


def check_session(request):
    return request.session.get('user', None)


def index(request):
    if check_session(request) is not None:
        if request.session.get('role') is 3:
            return render(request, './admin/index.html')
        return render(request, 'index.html')
    return render(request, 'login.html')


def login(request):
    return render(request, 'login.html', {})


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

        # print("Debug 1:" + str(username_input))
        # print("Debug 2:" + str(password_input))

    return HttpResponse(json.dumps(response), content_type="application/json")


def logout(request):
    response = {}
    if request.method == 'POST':
        del request.session['user']
        del request.session['role']
        request.session.flush()

    session_user = request.session.get('user', None)
    session_role = request.session.get('role', None)

    if session_user is None and session_role is None:
        response['status'] = 'success'
    else:
        response['status'] = 'fail'
        response['message'] = 'Sign Out failed. Please try again.'

    return HttpResponse(json.dumps(response), content_type="application/json")


# Admin
def admin_index(request):
    print(request.session.get('role'))
    if check_session(request) is not None:
        if request.session.get('role') is 3:
            return render(request, './admin/index.html')

        if request.session.get('role') is not 3:
            return render(request, 'index.html')

    return render(request, 'login.html')


def admin_bootstrap(request):
    response = {}
    error_message =[]

    if request.method == 'POST':
        if len(request.content_type) != 0:
            # Retrieve uploaded file and token
            token = csrf.get_token(request)
            try:
                file_uploaded = request.FILES['bootstrap_input']
            except KeyError:
                error_message.append("No file selected")

            if len(error_message) == 0:
                # Validate token and file
                if len(token) != 0 and is_zipfile(file_uploaded):
                    # Read the ZIP file
                    with ZipFile(file_uploaded, 'r') as z_file:
                        files_hash = {}
                        key_files_hash = files_hash.keys()

                        z_list = z_file.namelist()
                        if len(z_list) != 0:
                            # Proceed to clear database
                            clear_database(request)

                            # Get files listing
                            for listing in z_list:
                                # Insert into hash according to database schema and its constraints
                                if listing == 'user.csv':
                                    files_hash['1'] = 'user.csv'

                            if '1' in key_files_hash:
                                with z_file.open('user.csv', 'r') as csvfile:
                                    csvfile = io.TextIOWrapper(csvfile)
                                    contents = csv.reader(csvfile)
                                    for row in contents:
                                        if len(row) != 0 and row[0].lower() != 'userid':
                                            new_user = User(user_id=row[0], password=row[1], role=row[2])
                                            User.save(new_user)
                            else:
                                error_message.append("user.csv is needed")

                            if len(error_message) != 0:
                                # Proceed to next table insertion
                                print("Proceed!")
                        else:
                            error_message.append("Empty file")

                else:
                    if len(token) == 0:
                        error_message.append("Invalid token")
                    if is_zipfile(file_uploaded) is False:
                        error_message.append("Non ZIP file format")
        else:
            error_message.append("Invalid Content Type")

    if len(error_message) == 0:
        response['status'] = 'success'
        response['message'] = 'Database updated'
    else:
        response['status'] = 'fail'
        response['message'] = error_message

    return HttpResponse(json.dumps(response), content_type="application/json")


def clear_database(request):
    session_user = request.session.get('user', None)
    if session_user is not None:
        User.objects.all().exclude(user_id=session_user).delete()


# Student
def courseplanner(request):
    if check_session(request) is not None:
        return render(request, 'courseplanner.html')
    return render(request, 'login.html')


def recommendjob(request):
    if check_session(request) is not None:
        return render(request, 'recommendjob.html')
    return render(request, 'login.html')


def modulesearch(request):
    if check_session(request) is not None:
        return render(request, 'modulesearch.html')
    return render(request, 'login.html')


def userprofile(request):
    if check_session(request) is not None:
        return render(request, 'userprofile.html')
    return render(request, 'login.html')
