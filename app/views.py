import json
import csv
import io
from zipfile import *
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators import csrf
from app.models import *
from django.core.serializers.json import DjangoJSONEncoder


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
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

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
    if check_session(request) is not None:
        if request.session.get('role') is 3:
            return render(request, './admin/index.html')

        if request.session.get('role') is not 3:
            return render(request, 'index.html')

    return render(request, 'login.html')


def admin_bootstrap(request):
    response = {}
    error_message =[]
    duplicate_error_message = {}
    validation_error_message = {}

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
                        file_array = []
                        files_hash = {}
                        key_files_hash = files_hash.keys()

                        z_list = z_file.namelist()
                        z_list = sorted(z_list)
                        if len(z_list) != 0:
                            # Proceed to clear database
                            # clear_database(request)

                            # Get files listing
                            for listing in z_list:
                                # Insert into hash according to database schema and its constraints
                                if listing == 'user.csv':
                                    files_hash['1'] = listing
                                if listing == 'course.csv':
                                    files_hash['2'] = listing
                                if listing == 'student.csv':
                                    files_hash['3'] = listing
                                if listing == 'module.csv':
                                    files_hash['4'] = listing
                                if listing == 'prerequisite.csv':
                                    files_hash['5'] = listing
                                if listing == 'coursemapping.csv':
                                    files_hash['6'] = listing
                                if listing == 'coursespecialization.csv':
                                    files_hash['7'] = listing
                                if listing == 'mbti.csv':
                                    files_hash['8'] = listing
                                if listing == 'jobcategory.csv':
                                    files_hash['9'] = listing
                                if listing == 'interestsector.csv':
                                    files_hash['10'] = listing

                            if '3' in key_files_hash:
                                # Check for user.csv
                                if '1' not in key_files_hash:
                                    error_message.append("Missing: user.csv")

                                # Check if course table is empty in database
                                if check_table(Course) is None and '2' not in key_files_hash:
                                    error_message.append("Missing: course.csv")

                            if '1' not in key_files_hash:
                             error_message.append("Missing: user.csv")
                            if '2' not in key_files_hash:
                             error_message.append("Missing: course.csv")
                            if '3' not in key_files_hash:
                             error_message.append("Missing: student.csv")
                            if '4' not in key_files_hash:
                             error_message.append("Missing: module.csv")
                            if '5' not in key_files_hash:
                             error_message.append("Missing: prerequisite.csv")

                            if len(error_message) == 0:
                                for key in sorted(files_hash.keys()):
                                    file = files_hash[key]

                                    # Bootstrap [user.csv]
                                    if file == 'user.csv':
                                        status = bootstrap_user(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [course.csv]
                                    if file == 'course.csv':
                                        clear_database(Course)
                                        status = bootstrap_course(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [student.csv]
                                    if file == 'student.csv':
                                        status = bootstrap_student(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [module.csv]
                                    if file == 'module.csv':
                                        clear_database(Module)
                                        status = bootstrap_module(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [prerequisite.csv]
                                    if file == 'prerequisite.csv':
                                        clear_database(Prerequisite)
                                        status = bootstrap_prerequisite(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [coursemapping.csv]
                                    if file == 'coursemapping.csv':
                                        clear_database(CourseMapping)
                                        status = bootstrap_course_mapping(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [coursespecialization.csv]
                                    if file == 'coursespecialization.csv':
                                        clear_database(CourseSpecialization)
                                        status = bootstrap_course_specialization(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [mbti.csv]
                                    if file == 'mbti.csv':
                                        clear_database(Mbti)
                                        status = bootstrap_mbti(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [jobcategory.csv]
                                    if file == 'jobcategory.csv':
                                        clear_database(JobCategory)
                                        status = bootstrap_jobcategory(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error

                                    # Bootstrap [interestsector.csv]
                                    if file == 'interestsector.csv':
                                        clear_database(InterestSector)
                                        status = bootstrap_interestsector(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']

                                        if len(get_duplicate_error) != 0:
                                            duplicate_error_message[file] = get_duplicate_error
                                        if len(get_validation_error) != 0:
                                            validation_error_message[file] = get_validation_error
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
        response['duplicate'] = duplicate_error_message
        response['validation'] = validation_error_message
    else:
        response['status'] = 'fail'
        response['message'] = error_message

    return HttpResponse(json.dumps(response), content_type="application/json")


def check_table(model):
    try:
        return model.objects.all()
    except model.DoesNotExist:
        return None


def clear_database(model):
    model.objects.all().delete()


def models_get(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None


def bootstrap_user(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'userid':
                # Validations Required

                # Check for duplicate entry
                userid = row[0]
                existing_user = models_get(User, user_id=userid)
                if existing_user is None:
                    new_user = User(user_id=userid, password=row[1], role=row[2])
                    User.save(new_user)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_course(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_code':
                # Check for duplicate entry
                coursecode = row[0]
                existing_course = models_get(Course, course_code=coursecode)
                if existing_course is None:
                    new_course = Course(course_code=coursecode, course_name=row[1], no_of_modules=row[2])
                    Course.save(new_course)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_student(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'user_id':
                # Validations Required. <For Email>
                user = models_get(User, user_id=row[0])
                course = models_get(Course, course_code=row[7])
                mbti = models_get(Mbti, mbti_code=row[8])

                if user is not None:
                    if course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")
                    else:
                        # Check for duplicate entry
                        existing_student = models_get(Student, user_id=row[0])
                        if existing_student is None:
                            new_student = Student(user_id=user, name=row[1], course_specialization=row[2],current_year=row[3], current_semester=row[4], email=row[5], profile_picture=row[6], course_code=course, mbti_code=mbti)
                            Student.save(new_student)
                        else:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    validation_error.append("Line " + str(line_num) + ": no such user ID")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_module(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'module_code':
                # Check for duplicate entry
                existing_module = models_get(Module, module_name=row[1])
                if existing_module is None:
                    prerequiste_boolean = False
                    elective_boolean = False

                    if row[3].lower() == 'true':
                        prerequiste_boolean = True
                    if row[4].lower() == 'true':
                        elective_boolean = True

                    new_module = Module(module_code=row[0], module_name=row[1], school=row[2], has_prerequiste=prerequiste_boolean, is_elective=elective_boolean, specialisation=row[5], mod_description=row[6])
                    Module.save(new_module)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_prerequisite(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'module_code':
                a_module = models_get(Module, module_code=row[0])
                a_prerequisite = models_get(Module, module_code=row[1])

                if a_module is None or a_prerequisite is None:
                    validation_error.append("Line " + str(line_num) + ": no such module code")
                else:
                    # Check for duplicate entry
                    existing_prerequisite = models_get(Prerequisite, module_code=a_module)
                    if existing_prerequisite is None:
                        new_prerequisite = Prerequisite(module_code=a_module, prereq=a_prerequisite)
                        Prerequisite.save(new_prerequisite)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_course_mapping(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_mapping_id':
                a_course = models_get(Course, course_code=row[1])
                a_module = models_get(Module, module_code=row[2])

                if a_course is not None and a_module is not None:
                    # Check for duplicate entry
                    existing_course_mapping = models_get(CourseMapping, course_code=a_course, module_code=a_module, year=row[3], semester=row[4])
                    # Check for unique ID
                    existing_course_mapping_id = models_get(CourseMapping, course_mapping_id=row[0])

                    if existing_course_mapping is None and existing_course_mapping_id is None:
                        new_course_mapping = CourseMapping(course_mapping_id=row[0], course_code=a_course, module_code=a_module, year=row[3], semester=row[4])
                        CourseMapping.save(new_course_mapping)
                    else:
                        if existing_course_mapping_id is not None:
                            duplicates_error.append("Line " + str(line_num) + ": course mapping ID is not unique")
                        if existing_course_mapping is not None:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if a_course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")
                    if a_module is None:
                        validation_error.append("Line " + str(line_num) + ": no such module code")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_course_specialization(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_specialization_id':
                a_course = models_get(Course, course_code=row[1])

                if a_course is not None:
                    # Check for duplicate entry
                    existing_course_specialization = models_get(CourseSpecialization, course_code=a_course, course_specialization=row[2])
                    # Check for unique ID
                    existing_course_specialization_id = models_get(CourseSpecialization, course_specialization_id=row[0])

                    if existing_course_specialization is None and existing_course_specialization_id is None:
                        new_course_specialization = CourseSpecialization(course_specialization_id=row[0],  course_code=a_course, course_specialization=row[2])
                        CourseSpecialization.save(new_course_specialization)
                    else:
                        if existing_course_specialization_id is not None:
                            duplicates_error.append("Line " + str(line_num) + ": course specialization ID is not unique")
                        if existing_course_specialization is not None:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if a_course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_mbti(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'mbti_code':
                # Logical Validations
                mbtiCode = row[0]
                if len(mbtiCode) != 4:
                    validation_error.append("Line " + str(line_num) + ": MBTI code must be in length of 4")
                else:
                    # Check for duplicate entry - from unique ID
                    existing_mbti = models_get(Mbti, mbti_code=mbtiCode)
                    if existing_mbti is None:
                        new_mbti = Mbti(mbti_code=mbtiCode, mbti_description=row[1], possible_job_sector=row[2].replace(' &', ','))
                        Mbti.save(new_mbti)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_jobcategory(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'job_category_id':
                a_course = models_get(Course, course_code=row[2])

                if a_course is not None:
                    # Check for duplicate entry
                    existing_job_category = models_get(JobCategory, job_category=row[1], course_code=a_course)
                    # Check for duplicate unique ID
                    existing_job_category_id = models_get(JobCategory, job_category_id=row[0])

                    if existing_job_category is None and existing_job_category_id is None:
                        new_job_category = JobCategory(job_category_id=row[0],  job_category=row[1], course_code=a_course)
                        JobCategory.save(new_job_category)
                    else:
                        if existing_job_category_id is not None:
                            duplicates_error.append("Line " + str(line_num) + ": job category ID is not unique")
                        if existing_job_category is not None:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if a_course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


def bootstrap_interestsector(z_file, file):
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file)
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'interest_sector_id':
                # Logical Validation - Check if id is integer
                interestSectorId = row[0]
                if interestSectorId.isdigit():
                    # Check for duplicate entry
                    existing_interest_sector = models_get(InterestSector, personal_interest_sector=row[1])
                    # Check for duplicate unique ID
                    existing_interest_sector_id = models_get(InterestSector, interest_sector_id=interestSectorId)

                    if existing_interest_sector is None and existing_interest_sector_id is None:
                        new_interest_sector = InterestSector(interest_sector_id=interestSectorId,  personal_interest_sector=row[1])
                        InterestSector.save(new_interest_sector)
                    else:
                        if existing_interest_sector_id is not None:
                            duplicates_error.append("Line " + str(line_num) + ": interest sector ID is not unique")
                        if existing_interest_sector is not None:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    validation_error.append("Line " + str(line_num) + ": interest sector ID is not integer")

    status = {'duplicate': duplicates_error, 'validation': validation_error}
    return status


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
        return render(request, 'userprofile.html', student_info(request))
    return render(request, 'login.html')


def personalinterest(request):
    if check_session(request) is not None:
        return render(request, 'personalinterest.html')
    return render(request, 'login.html')


def transitionjobpage(request):
    if check_session(request) is not None:
        return render(request, 'transitionjobpage.html')
    return render(request, 'login.html')


def courserequirement(request):
    if check_session(request) is not None:
        return render(request, 'courserequirement.html', student_info(request))
    return render(request, 'login.html')


def student_info(request):
    current_student = {}
    student = Student.objects.get(user_id_id=request.session.get('user'))
    course = Course.objects.get(course_code=student.course_code_id)
    coursemapping = CourseMapping.objects.filter(course_code_id=student.course_code_id)

    module = {}
    for mod in coursemapping:
        module.update({CourseMapping.objects.filter(module_code_id=mod.module_code_id):{Module.objects.get(module_code=mod.module_code_id): str(mod.year) +  str(mod.semester)}})
    current_student['student'] = student
    current_student['course'] = course
    current_student['module'] = module
    return current_student


def modsearch(request):
    response = {}
    if request.method == 'POST':
        search_input = request.POST.get('modsearch')
        if not search_input:
            response['results'] = ''
        else:
            results = Module.objects.filter(module_name__icontains=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description') | \
                    Module.objects.filter(specialisation__search=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description') | \
                    Module.objects.filter(mod_description__search=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description')
            response['results'] = list(results)
            response['searchinput'] = search_input
    return HttpResponse(json.dumps(response), content_type="application/json")


def modcompare(request):
    response = {}
    modname = request.GET.get('modname')
    mod_des = Module.objects.filter(module_name=modname).values('mod_description')
    response['results'] = list(mod_des)
    return HttpResponse(json.dumps(response), content_type="application/json")


def specialisedropdown(request):
    response = {}
    course_specialise = CourseSpecialization.objects.values('course_specialization')
    response['results'] = list(course_specialise)
    return HttpResponse(json.dumps(response), content_type="application/json")


def specialisechoice(request):
    response = {}
    specialise = request.GET.get('specialise')
    specialise_mod = Module.objects.filter(specialisation=specialise)
    special_mod_year = {}
    for mod in specialise_mod:
        special_mod_year.update({mod.module_name:CourseMapping.objects.filter(module_code_id=mod.module_code).values('year')})

    response['results'] = list(special_mod_year)
    print(response['results'])
    return HttpResponse(json.dumps(response), content_type="application/json")



def personalinterestsectordropdown(request):
    response = {}
    data = []
    sectors_array = InterestSector.objects.values('personal_interest_sector')
    for sector in sectors_array:
        data.append(sector['personal_interest_sector'])
    response['results'] = data
    return HttpResponse(json.dumps(response), content_type="application/json")


def interestinput(request):
    response = {}
    data = []
    if request.method == 'POST':
        user_id = request.session.get('user')
        interest_input = request.POST.getlist('interestarray[]')

        if len(interest_input) == 0:
            response['status'] = 'fail'
            response['message'] = 'Empty input'
        else:
            # Save it to database
            for interest in interest_input:
                existing_user = models_get(User, user_id=user_id)
                existing_interest = models_get(InterestSector, personal_interest_sector=interest)
                new_student_interest = StudentInterestSector(user_id=existing_user, personal_interest_sector=existing_interest)
                StudentInterestSector.save(new_student_interest)
            response['status'] = 'success'
            response['message'] = 'Interests updated'

    return HttpResponse(json.dumps(response), content_type="application/json")


def retrievestudentinterest(request):
    response = {}
    user_id = request.session.get('user')
    existing_user = models_get(User, user_id=user_id)
    indicated_interests_id = StudentInterestSector.objects.filter(user_id_id=existing_user).values('personal_interest_sector_id')
    jobs = []
    for interest in indicated_interests_id:
        indicated_id = interest['personal_interest_sector_id']
        sector = models_get(InterestSector, interest_sector_id=indicated_id).personal_interest_sector
        job = Job.objects.filter(job_interest=sector).values()
        jobs.append(list(job))
        # print(jobs)

    serialized_q = json.dumps(list(jobs), cls=DjangoJSONEncoder)
    response['results'] = serialized_q
    return HttpResponse(json.dumps(response), content_type="application/json")


