import json
import csv
import io
from zipfile import *
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators import csrf
from app.models import *
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict


def check_session(request):
    return request.session.get('user', None)


def index(request):
    if check_session(request) is not None:
        if request.session.get('role') is 3:
            return render(request, './admin/index.html')
        student = Student.objects.get(user_id_id=request.session.get('user'))
        interest = StudentInterestSector.objects.filter(user_id_id=student.user_id_id)
        if not interest:
            return render(request, 'transitionjobpage.html')
        else:
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
                                    files_hash['01'] = listing
                                if listing == 'course.csv':
                                    files_hash['02'] = listing
                                if listing == 'student.csv':
                                    files_hash['03'] = listing
                                if listing == 'module.csv':
                                    files_hash['04'] = listing
                                if listing == 'prerequisite.csv':
                                    files_hash['05'] = listing
                                if listing == 'coursemapping.csv':
                                    files_hash['06'] = listing
                                if listing == 'coursespecialization.csv':
                                    files_hash['07'] = listing
                                if listing == 'mbti.csv':
                                    files_hash['08'] = listing
                                if listing == 'jobcategory.csv':
                                    files_hash['09'] = listing
                                if listing == 'interestsector.csv':
                                    files_hash['10'] = listing
                                if listing == 'specializationmodule.csv':
                                    files_hash['11'] = listing
                                if listing == 'electivemodule.csv':
                                    files_hash['12'] = listing

                            if '03' in key_files_hash:
                                # Check for user.csv
                                if '01' not in key_files_hash:
                                    error_message.append("Missing: user.csv")

                                # Check if course table is empty in database
                                course_queryset = check_table(Course)
                                if (course_queryset is None or len(course_queryset) == 0) and '02' not in key_files_hash:
                                    error_message.append("Missing: course.csv")

                            if len(error_message) == 0:
                                for key in sorted(files_hash.keys()):
                                    file = files_hash[key]

                                    # Bootstrap [user.csv]
                                    if file == 'user.csv':
                                        status = bootstrap_user(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            User.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [course.csv]
                                    if file == 'course.csv':
                                        status = bootstrap_course(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(Course)
                                            Course.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [student.csv]
                                    if file == 'student.csv':
                                        status = bootstrap_student(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            Student.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [module.csv]
                                    if file == 'module.csv':
                                        status = bootstrap_module(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(Module)
                                            Module.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [prerequisite.csv]
                                    if file == 'prerequisite.csv':
                                        status = bootstrap_prerequisite(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(Prerequisite)
                                            Prerequisite.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [coursemapping.csv]
                                    if file == 'coursemapping.csv':
                                        status = bootstrap_course_mapping(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(CourseMapping)
                                            CourseMapping.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [coursespecialization.csv]
                                    if file == 'coursespecialization.csv':
                                        status = bootstrap_course_specialization(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(CourseSpecialization)
                                            CourseSpecialization.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [mbti.csv]
                                    if file == 'mbti.csv':
                                        status = bootstrap_mbti(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(Mbti)
                                            Mbti.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [jobcategory.csv]
                                    if file == 'jobcategory.csv':
                                        status = bootstrap_jobcategory(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(JobCategory)
                                            JobCategory.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [interestsector.csv]
                                    if file == 'interestsector.csv':
                                        status = bootstrap_interest_sector(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(InterestSector)
                                            InterestSector.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [specializationmodule.csv]
                                    if file == 'specializationmodule.csv':
                                        status = bootstrap_specialization_module(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            clear_database(SpecializationModule)
                                            SpecializationModule.objects.bulk_create(get_content)
                                        else:
                                            if len(get_duplicate_error) != 0:
                                                duplicate_error_message[file] = get_duplicate_error
                                            if len(get_validation_error) != 0:
                                                validation_error_message[file] = get_validation_error

                                    # Bootstrap [electivemodule.csv]
                                    if file == 'electivemodule.csv':
                                        status = bootstrap_elective_module(z_file, file)
                                        get_duplicate_error = status['duplicate']
                                        get_validation_error = status['validation']
                                        get_content = status['content']

                                        if len(get_duplicate_error) == 0 and len(get_validation_error) == 0:
                                            # No errors found. Proceed to add contents to database
                                            # clear_database(ElectiveModule)
                                            ElectiveModule.objects.bulk_create(get_content)
                                        else:
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
        response['message'] = 'Database is updated!'
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
    user_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'userid':
                # Validations Required

                # Check for duplicate entry
                userid = row[0]
                existing_user_database = models_get(User, user_id=userid)
                existing_user_csv = False
                for user_object in user_array:
                    user_object_id = user_object.user_id
                    if user_object_id == userid:
                        existing_user_csv = True

                if existing_user_csv is False and existing_user_database is None:
                    # User ID is unique
                    new_user = User(user_id=userid, password=row[1], role=row[2])
                    user_array.append(new_user)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': user_array}
    return status


def bootstrap_course(z_file, file):
    course_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_code':
                # Check for duplicate entry
                coursecode = row[0]
                existing_course_database = models_get(Course, course_code=coursecode)
                existing_course_csv = False
                for course_object in course_array:
                    course_object_code = course_object.course_code
                    if course_object_code == coursecode:
                        existing_course_csv = True

                if existing_course_csv is False and existing_course_database is None:
                    # Course Code is unique
                    new_course = Course(course_code=coursecode, course_name=row[1], no_of_modules=row[2])
                    course_array.append(new_course)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': course_array}
    return status


def bootstrap_student(z_file, file):
    student_array = []
    duplicates_error = []
    validation_error = []

    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'user_id':
                # Validations Required. <For Email>
                user = models_get(User, user_id=row[0])
                course = models_get(Course, course_code=row[3])
                mbti = models_get(Mbti, mbti_code=row[9])
                courseSpecialization = models_get(CourseSpecialization, course_specialization_id=row[10])

                if user is not None:
                    if course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")
                    else:
                        # Check for duplicate entry
                        existing_student_database = models_get(Student, user_id=row[0])
                        existing_student_csv = False
                        for student_object in student_array:
                            student_object_id = student_object.user_id
                            if student_object_id == row[0]:
                                existing_student_csv = True

                        if existing_student_csv is False and existing_student_database is None:
                            # Student User ID is unique
                            new_student = Student(user_id=user, name=row[1], email=row[2], course_code=course, current_year=row[4], current_semester=row[5], choose_capstone=row[6], choose_internship=row[7], profile_picture=row[8], mbti_code=mbti, course_specialization=courseSpecialization)
                            student_array.append(new_student)
                        else:
                            duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    validation_error.append("Line " + str(line_num) + ": no such user ID")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': student_array}
    return status


def bootstrap_module(z_file, file):
    module_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'module_code':
                # Check for duplicate entry
                existing_module_database = models_get(Module, module_code=row[0])
                existing_module_csv = False
                for module_object in module_array:
                    module_object_id = module_object.module_code
                    if module_object_id == row[0]:
                        existing_module_csv = True

                if existing_module_csv is False and existing_module_database is None:
                    # Module Code is unique
                    prerequiste_boolean = False
                    if row[3].lower() == 'true' or row[3] == '1':
                        prerequiste_boolean = True

                    new_module = Module(module_code=row[0], module_name=row[1], school=row[2], has_prerequiste=prerequiste_boolean, mod_description=row[4])
                    module_array.append(new_module)
                else:
                    duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': module_array}
    return status


def bootstrap_prerequisite(z_file, file):
    prerequisite_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'prerequisite_id':
                a_module = models_get(Module, module_code=row[1])
                a_prerequisite = models_get(Module, module_code=row[2])

                if a_module is None or a_prerequisite is None:
                    validation_error.append("Line " + str(line_num) + ": no such module code")
                else:
                    # Check for duplicate entry
                    existing_prerequisite_database_id = models_get(Prerequisite, prerequisite_id=row[0])
                    existing_prerequisite_database_other = models_get(Prerequisite, module_code=a_module, prereq=a_prerequisite)
                    existing_prerequisite_csv = False
                    for prerequisite_object in prerequisite_array:
                        prerequisite_object_id = prerequisite_object.prerequisite_id
                        prerequisite_object_module = prerequisite_object.module_code
                        prerequisite_object_prereq = prerequisite_object.prereq
                        if prerequisite_object_id == row[0] or prerequisite_object_module == a_module or prerequisite_object_prereq == a_prerequisite:
                            existing_prerequisite_csv = True

                    if existing_prerequisite_csv is False and existing_prerequisite_database_id is None and existing_prerequisite_database_other is None:
                        # Prerequisite ID is unique. No duplicates for module and prerequisite.
                        new_prerequisite = Prerequisite(prerequisite_id=row[0], module_code=a_module, prereq=a_prerequisite)
                        prerequisite_array.append(new_prerequisite)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': prerequisite_array}
    return status


def bootstrap_course_mapping(z_file, file):
    course_mapping_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_mapping_id':
                a_course = models_get(Course, course_code=row[1])
                a_module = models_get(Module, module_code=row[2])

                if a_course is not None and a_module is not None:
                    # Check for duplicate entry
                    existing_course_mapping_database_id = models_get(CourseMapping, course_mapping_id=row[0])
                    existing_course_mapping_database_other = models_get(CourseMapping, course_code=a_course, module_code=a_module, year=row[3], semester=row[4])
                    existing_course_mapping_csv = False
                    for course_mapping_object in course_mapping_array:
                        course_mapping_object_id = course_mapping_object.course_mapping_id
                        course_mapping_object_course = course_mapping_object.course_code
                        course_mapping_object_module = course_mapping_object.module_code
                        course_mapping_object_year = course_mapping_object.year
                        course_mapping_object_semester = course_mapping_object.semester
                        if course_mapping_object_id == row[0] or (course_mapping_object_course == a_course and course_mapping_object_module == a_module and course_mapping_object_year == row[3] and course_mapping_object_semester == row[4]):
                            existing_course_mapping_csv = True

                    if existing_course_mapping_csv is False and existing_course_mapping_database_id is None and existing_course_mapping_database_other is None:
                        # Course Mapping ID is unique. No duplicates for the other columns.
                        new_course_mapping = CourseMapping(course_mapping_id=row[0], course_code=a_course, module_code=a_module, year=row[3], semester=row[4])
                        course_mapping_array.append(new_course_mapping)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if a_course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course code")
                    if a_module is None:
                        validation_error.append("Line " + str(line_num) + ": no such module code")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': course_mapping_array}
    return status


def bootstrap_course_specialization(z_file, file):
    course_specialization_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'course_specialization_id':
                a_course = models_get(Course, course_code=row[1])

                if a_course is not None:
                    # Check for duplicate entry
                    existing_course_specialization_database_id = models_get(CourseSpecialization, course_specialization_id=row[0])
                    existing_course_specialization_database_other = models_get(CourseSpecialization, course_code=a_course, course_specialization=row[2])
                    existing_course_specialization_csv = False
                    for course_specialization_object in course_specialization_array:
                        course_specialization_object_id = course_specialization_object.course_specialization_id
                        course_specialization_object_course = course_specialization_object.course_code
                        course_specialization_object_desc = course_specialization_object.course_specialization
                        if course_specialization_object_id == row[0] or (course_specialization_object_course == a_course and course_specialization_object_desc == row[2]):
                            existing_course_specialization_csv = True

                    if existing_course_specialization_csv is False and existing_course_specialization_database_id is None and existing_course_specialization_database_other is None:
                        # Course Specialization ID is unique. No duplicates for the other columns.
                        new_course_specialization = CourseSpecialization(course_specialization_id=row[0],  course_code=a_course, course_specialization=row[2])
                        course_specialization_array.append(new_course_specialization)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    validation_error.append("Line " + str(line_num) + ": no such course code")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': course_specialization_array}
    return status


def bootstrap_mbti(z_file, file):
    mbti_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
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
                    existing_mbti_database = models_get(Mbti, mbti_code=mbtiCode)
                    existing_mbti_csv = False
                    for mbti_object in mbti_array:
                        mbti_object_code = mbti_object.mbti_code
                        if mbti_object_code == mbtiCode:
                            existing_mbti_csv = True

                    if existing_mbti_csv is False and existing_mbti_database is None:
                        # MBTI Code is unique.
                        new_mbti = Mbti(mbti_code=mbtiCode, mbti_description=row[1], possible_job_sector=row[2].replace(' &', ','))
                        mbti_array.append(new_mbti)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': mbti_array}
    return status


def bootstrap_jobcategory(z_file, file):
    jobcategory_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'job_category_id':
                a_course = models_get(Course, course_code=row[2])

                if a_course is not None:
                    # Check for duplicate entry
                    existing_job_category_database_id = models_get(JobCategory, job_category_id=row[0])
                    existing_job_category_database_other = models_get(JobCategory, job_category=row[1], course_code=a_course)
                    existing_job_category_csv = False
                    for job_category_object in jobcategory_array:
                        job_category_object_id = job_category_object.job_category_id
                        job_category_object_desc = job_category_object.job_category
                        job_category_object_course = job_category_object.course_code
                        if job_category_object_id == row[0] or (job_category_object_desc == row[1] and job_category_object_course == row[2]):
                            existing_job_category_csv = True

                    if existing_job_category_csv is False and existing_job_category_database_id is None and existing_job_category_database_other is None:
                        # Job Category ID is unique. No duplicates for the other columns.
                        new_job_category = JobCategory(job_category_id=row[0],  job_category=row[1], course_code=a_course)
                        jobcategory_array.append(new_job_category)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    validation_error.append("Line " + str(line_num) + ": no such course code")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': jobcategory_array}
    return status


def bootstrap_interest_sector(z_file, file):
    interest_sector_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'interest_sector_id':
                # Logical Validation - Check if id is integer
                interestSectorId = row[0]
                course_specialization_id = row[2]
                a_course_specialization = models_get(CourseSpecialization, course_specialization_id=course_specialization_id)

                if interestSectorId.isdigit() and len(course_specialization_id) != 0 and a_course_specialization is not None:
                    # Check for duplicate entry
                    existing_interest_sector_database_id = models_get(InterestSector, interest_sector_id=interestSectorId)
                    existing_interest_sector_database_other = models_get(InterestSector, personal_interest_sector=row[1], course_specialization_id=row[2])
                    existing_interest_sector_csv = False
                    for interest_sector_object in interest_sector_array:
                        interest_sector_object_id = interest_sector_object.interest_sector_id
                        interest_sector_object_desc = interest_sector_object.personal_interest_sector
                        interest_sector_object_specialization = interest_sector_object.course_specialization_id
                        if interest_sector_object_id == interestSectorId or (interest_sector_object_desc == row[1] and interest_sector_object_specialization == row[2]):
                            existing_interest_sector_csv = True

                    if existing_interest_sector_csv is False and existing_interest_sector_database_id is None and existing_interest_sector_database_other is None:
                        # Interest Sector ID is unique. No duplicates for the other columns.
                        new_interest_sector = InterestSector(interest_sector_id=interestSectorId,  personal_interest_sector=row[1], course_specialization_id=a_course_specialization)
                        interest_sector_array.append(new_interest_sector)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                elif interestSectorId.isdigit() and len(course_specialization_id) == 0 and a_course_specialization is None:
                    # Check for duplicate entry
                    existing_interest_sector_database_id = models_get(InterestSector, interest_sector_id=interestSectorId)
                    existing_interest_sector_database_other = models_get(InterestSector, personal_interest_sector=row[1], course_specialization_id=row[2])
                    existing_interest_sector_csv = False
                    for interest_sector_object in interest_sector_array:
                        interest_sector_object_id = interest_sector_object.interest_sector_id
                        interest_sector_object_desc = interest_sector_object.personal_interest_sector
                        interest_sector_object_specialization = interest_sector_object.course_specialization_id
                        if interest_sector_object_id == interestSectorId or (interest_sector_object_desc == row[1] and interest_sector_object_specialization == row[2]):
                            existing_interest_sector_csv = True

                    if existing_interest_sector_csv is False and existing_interest_sector_database_id is None and existing_interest_sector_database_other is None:
                        # Interest Sector ID is unique. No duplicates for the other columns.
                        new_interest_sector = InterestSector(interest_sector_id=interestSectorId,  personal_interest_sector=row[1])
                        interest_sector_array.append(new_interest_sector)
                else:
                    if interestSectorId.isdigit() is False:
                        validation_error.append("Line " + str(line_num) + ": interest sector ID is not an integer")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': interest_sector_array}
    return status


def bootstrap_specialization_module(z_file, file):
    specialization_module_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'specialization_module_id':
                # Logical Validation - Check if id is integer
                specializationModuleId = row[0]
                a_course_specialization = models_get(CourseSpecialization, course_specialization_id=row[1])
                a_module = models_get(Module, module_code=row[2])

                if specializationModuleId.isdigit() and a_course_specialization is not None and a_module is not None:
                    # Check for duplicate entry
                    existing_specialization_module_database_id = models_get(SpecializationModule, specialization_module_id=specializationModuleId)
                    existing_specialization_module_database_other = models_get(SpecializationModule, course_specialization_id=row[1], module_code=row[2])
                    existing_specialization_module_csv = False
                    for specialization_module_object in specialization_module_array:
                        specialization_module_object_id = specialization_module_object.specialization_module_id
                        specialization_module_object_course = specialization_module_object.course_specialization_id
                        specialization_module_object_module = specialization_module_object.module_code
                        if specialization_module_object_id == specializationModuleId or (specialization_module_object_course == row[1] and specialization_module_object_module == row[2]):
                            existing_specialization_module_csv = True

                    if existing_specialization_module_csv is False and existing_specialization_module_database_id is None and existing_specialization_module_database_other is None:
                        # Specialization Module ID is unique. No duplicates for the other columns.
                        new_specialization_module = SpecializationModule(specialization_module_id=specializationModuleId, course_specialization_id=a_course_specialization, module_code=a_module)
                        specialization_module_array.append(new_specialization_module)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if specializationModuleId.isdigit() is False:
                        validation_error.append("Line " + str(line_num) + ": specialization module ID is not an integer")
                    if a_course_specialization is None:
                        validation_error.append("Line " + str(line_num) + ": no such course specialization")
                    if a_module is None:
                        validation_error.append("Line " + str(line_num) + ": no such module")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': specialization_module_array}
    return status


def bootstrap_elective_module(z_file, file):
    elective_module_array = []
    duplicates_error = []
    validation_error = []
    with z_file.open(file, 'r') as csv_file:
        csv_file = io.TextIOWrapper(csv_file, encoding='utf-8')
        contents = csv.reader(csv_file)

        line_num = 0
        for row in contents:
            line_num += 1
            if len(row) != 0 and row[0].lower() != 'elective_code':
                # Logical Validation - Check if id is integer
                elective_module_id = row[0]
                a_course = models_get(Course, course_code=row[1])
                a_module = models_get(Module, module_code=row[2])

                if elective_module_id.isdigit() and a_course is not None and a_module is not None:
                    # Check for duplicate entry
                    existing_elective_module_database_id = models_get(ElectiveModule, elective_code=elective_module_id)
                    existing_elective_module_database_other = models_get(ElectiveModule, course_code=row[1], module_code=row[2])
                    existing_elective_module_csv = False
                    for elective_module_object in elective_module_array:
                        elective_module_object_id = elective_module_object.elective_code
                        elective_module_object_course = elective_module_object.course_code
                        elective_module_object_module = elective_module_object.module_code
                        if elective_module_object_id == elective_module_id or (elective_module_object_course == row[1] and elective_module_object_module == row[2]):
                            existing_specialization_module_csv = True

                    if existing_elective_module_csv is False and existing_elective_module_database_id is None and existing_elective_module_database_other is None:
                        # Elective Module ID is unique. No duplicates for the other columns.
                        new_elective_module = ElectiveModule(elective_code=elective_module_id, course_code=a_course, module_code=a_module)
                        elective_module_array.append(new_elective_module)
                    else:
                        duplicates_error.append("Line " + str(line_num) + ": duplicate entry")
                else:
                    if elective_module_id.isdigit() is False:
                        validation_error.append("Line " + str(line_num) + ": elective module ID is not an integer")
                    if a_course is None:
                        validation_error.append("Line " + str(line_num) + ": no such course")
                    if a_module is None:
                        validation_error.append("Line " + str(line_num) + ": no such module")

    status = {'duplicate': duplicates_error, 'validation': validation_error, 'content': elective_module_array}
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
        student = Student.objects.get(user_id_id=request.session.get('user'))
        interests = StudentInterestSector.objects.filter(user_id_id=student.user_id_id)

        interestnames = []
        for interest in interests:
            specialise = models_get(InterestSector,interest_sector_id=interest.personal_interest_sector_id)
            interestname = CourseSpecialization.objects.filter(course_specialization_id=specialise.course_specialization_id_id).values('course_specialization')
            interestnames.append(interestname)
        return render(request, 'personalinterest.html',{'interestnames': interestnames})
    return render(request, 'login.html')


def transitionjobpage(request):
    if check_session(request) is not None:
        student = Student.objects.get(user_id_id=request.session.get('user'))
        interest = StudentInterestSector.objects.filter(user_id_id=student.user_id_id)
        if interest is None:
            return render(request, 'transitionjobpage.html')
        else:
            return render(request, 'index.html')
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
    jobinterest = request.GET.get('jobinterest')

    module11 = {}
    module12 = {}
    module21 = {}
    module22 = {}
    module31 = {}
    module32 = {}

    for mod in coursemapping:
        module = Module.objects.get(module_code=mod.module_code_id)
        # module.update({CourseMapping.objects.filter(module_code_id=mod.module_code_id):{Module.objects.get(module_code=mod.module_code_id): str(mod.year) +  str(mod.semester)}})
        if mod.year is 1:
            if mod.semester is 1:
                module11.update({module.module_code: module.module_name})
            else:
                module12.update({module.module_code: module.module_name})
        elif mod.year is 2:
            if mod.semester is 1:
                module21.update({module.module_code: module.module_name})
            else:
                module22.update({module.module_code: module.module_name})
        elif mod.year is 3:
            if mod.semester is 1:
                module31.update({module.module_code: module.module_name})
            else:
                module32.update({module.module_code: module.module_name})

    current_student['jobinterest'] = jobinterest
    current_student['student'] = student
    current_student['course'] = course
    current_student['module11'] = module11
    current_student['module12'] = module12
    current_student['module21'] = module21
    current_student['module22'] = module22
    current_student['module31'] = module31
    current_student['module32'] = module32
    return current_student


def modsearch(request):
    response = {}
    if request.method == 'POST':
        search_input = request.POST.get('modsearch')
        if not search_input:
            response['results'] = ''
        else:
            # results = Module.objects.filter(module_name__icontains=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description') | \
            #         Module.objects.filter(specialisation__search=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description') | \
            #         Module.objects.filter(mod_description__search=search_input).values('module_code', 'module_name', 'school', 'has_prerequiste', 'is_elective', 'specialisation', 'mod_description')
            results = Module.objects.filter(module_name__icontains=search_input).values('module_code', 'module_name',
                                                                                        'school', 'has_prerequiste',
                                                                                        'mod_description')
            response['results'] = list(results)
            response['searchinput'] = search_input
    return HttpResponse(json.dumps(response), content_type="application/json")


def modcompare(request):
    response = {}
    student = Student.objects.get(user_id_id=request.session.get('user'))
    course = Course.objects.get(course_code=student.course_code_id)
    specialise_mods_id = []
    specialise_mods = []

    if request.method == 'POST':
        specialise = request.POST.get('specialisechoice')
        request.session['specialisechoice'] = specialise

    if request.method == 'GET':
        modname = request.GET.get('modname')
        module = Module.objects.get(module_name=modname)

        if 'specialisechoice' in request.session:
            chosen_specialise = request.session['specialisechoice']
            if module.module_code is 139:
                coursespecialization = CourseSpecialization.objects.filter(course_code_id=course.course_code)
                if coursespecialization is not None:
                    special_course = CourseSpecialization.objects.get(course_specialization=chosen_specialise)
                    for special in coursespecialization:
                        cc = special.course_specialization_id
                        if cc == special_course.course_specialization_id:
                            specialise_mods_id.append(SpecializationModule.objects.filter(course_specialization_id_id=cc))
            # else:
            #     if 'specialisechoice' in request.session:
            #         del request.session['specialisechoice']

        for special in specialise_mods_id:
            for item in special:
                specialmod = Module.objects.get(module_code=item.module_code_id)
                specialise_mods.append(model_to_dict(specialmod))

        response['des'] = module.mod_description
        response['specialise_mods'] = specialise_mods

    return HttpResponse(json.dumps(response), content_type="application/json")


def specialisedropdown(request):
    response = {}
    student = Student.objects.get(user_id_id=request.session.get('user'))
    course = Course.objects.get(course_code=student.course_code_id)

    course_specialise = []
    coursespecialization = CourseSpecialization.objects.filter(course_code_id=course.course_code)
    if len(coursespecialization) is not 0:
        for special in coursespecialization:
            cc = special.course_specialization
            course_specialise.append(cc)

    response['results'] = course_specialise
    return HttpResponse(json.dumps(response), content_type="application/json")


def specialisechoice(request):
    response = {}
    specialise = request.GET.get('specialise')
    # specialise_mod = Module.objects.filter(specialisation=specialise)
    special_mod_year = {}
    # for mod in specialise_mod:
    #     special_mod_year.update({mod.module_name:CourseMapping.objects.filter(module_code_id=mod.module_code).values('year')})

    response['results'] = list(special_mod_year)
    #print(response['results'])
    return HttpResponse(json.dumps(response), content_type="application/json")


def interestinput(request):
    response = {}
    data = []
    if request.method == 'POST':
        user_id = request.session.get('user')
        interest_input = request.POST.getlist('interestarray[]')
        student_interest_array = []

        if len(interest_input) == 0:
            response['status'] = 'fail'
            response['message'] = 'Empty input'
        else:
            try:
                InterestSector.objects.get(personal_interest_sector=interest_input[0])
                # Save it to database
                # Check if student and interest is in student and personal interest database
                existing_user = models_get(User, user_id=user_id)
                existing_interest = models_get(InterestSector, personal_interest_sector=interest_input[0])
                if existing_user is not None and existing_interest is not None:
                    # Delete all existing interests under the student
                    StudentInterestSector.objects.filter(user_id=existing_user).delete()
                    new_student_interest = StudentInterestSector(user_id=existing_user, personal_interest_sector=existing_interest)
                    student_interest_array.append(new_student_interest)
            except:
                # Save it to database
                try:
                    for interest in interest_input:
                        interestchoice = json.loads(interest)
                        for sector in interestchoice:
                            # Check if student and interest is in student and personal interest database
                            existing_user = models_get(User, user_id=user_id)
                            interest_code = CourseSpecialization.objects.get(course_specialization=sector)
                            existing_interest = models_get(InterestSector, course_specialization_id_id=interest_code.course_specialization_id)
                            if existing_user is not None and existing_interest is not None:
                                # Delete all existing interests under the student
                                StudentInterestSector.objects.filter(user_id=existing_user).delete()
                                new_student_interest = StudentInterestSector(user_id=existing_user, personal_interest_sector_id=existing_interest.interest_sector_id)
                                student_interest_array.append(new_student_interest)
                except:
                    response['error'] = 'Please select a specialization.'
            if 'error' not in response:
                StudentInterestSector.objects.bulk_create(student_interest_array)
            response['message'] = 'Interests updated! Please wait to be redirected...'
            response['status'] = 'success'

    return HttpResponse(json.dumps(response), content_type="application/json")


# have repeated code from getstudentinterest
def retrievestudentinterest(request):
    response = {}
    user_id = request.session.get('user')
    existing_user = models_get(User, user_id=user_id)
    interestFilter = request.GET.get('interestFilter')
    gov = []
    private = []

    if interestFilter is not None:
        private = Job.objects.filter(job_interest=interestFilter, job_id__icontains='JS-').values()
        gov = Job.objects.filter(job_interest=interestFilter, job_id__icontains='CG-').values()
        # for diploma related jobs
        if len(private) == 0 and len(gov) == 0:
            print('entered diploma')
            private = Job.objects.filter(job_keyword=interestFilter, job_id__icontains='JS-').values()
            gov = Job.objects.filter(job_interest=interestFilter, job_id__icontains='CG-').values()
    else:
        indicated_interests_id = StudentInterestSector.objects.filter(user_id_id=existing_user).values('personal_interest_sector_id')
        for interest in indicated_interests_id:
            indicated_id = interest['personal_interest_sector_id']
            try:
                sector_id = models_get(InterestSector, interest_sector_id=indicated_id).course_specialization_id_id
                sector = models_get(CourseSpecialization, course_specialization_id=sector_id).course_specialization
            except:
                sector = models_get(InterestSector, interest_sector_id=indicated_id).personal_interest_sector
            private = Job.objects.filter(job_interest=sector, job_id__icontains='CG-').values()
            gov = Job.objects.filter(job_keyword=interestFilter, job_id__icontains='JS-').values()
    print(len(gov))
    print(len(private))
    serialized_q1 = json.dumps(list(gov), cls=DjangoJSONEncoder)
    response['gov'] = serialized_q1
    serialized_q2 = json.dumps(list(private), cls=DjangoJSONEncoder)
    response['private'] = serialized_q2
    return HttpResponse(json.dumps(response), content_type="application/json")


def getstudentinterest(request):
    user_id = request.session.get('user')
    existing_user = models_get(User, user_id=user_id)
    existing_student = models_get(Student, user_id=user_id)
    indicated_interests_id = StudentInterestSector.objects.filter(user_id_id=existing_user).values(
        'personal_interest_sector_id')
    sector = '<optgroup label="Potential Job Positions Based on Personal Interest">'
    for interest in indicated_interests_id:
        indicated_id = interest['personal_interest_sector_id']
        interest_name = models_get(InterestSector, interest_sector_id=indicated_id).personal_interest_sector
        specialise_id = models_get(InterestSector, interest_sector_id=indicated_id).course_specialization_id_id
        if specialise_id is not None:
            interest_name = models_get(CourseSpecialization, course_specialization_id=specialise_id).course_specialization
        sector += '<option value="' + interest_name + '">' + interest_name + '</option>'
    # print(sector)
    sector += '<optgroup label="Potential Job Positions Based on Diploma">'
    jobsectors = JobCategory.objects.filter(course_code_id=existing_student.course_code_id).values(
        'job_category')
    for jobinterest in jobsectors:
        jobinterestname = jobinterest['job_category']
        sector += '<option value="' + jobinterestname + '">' + jobinterestname + '</option>'
    return HttpResponse(json.dumps(sector), content_type="application/json")


def personalinterestsectordropdown(request):
    response = {}
    data = []
    sectors_array = InterestSector.objects.values('personal_interest_sector')
    for sector in sectors_array:
        if sector['personal_interest_sector'] not in data:
            data.append(sector['personal_interest_sector'])
    response['results'] = data
    return HttpResponse(json.dumps(response), content_type="application/json")


def getcoursespecialization(request):
    response = {}
    data = []
    sector = request.GET.get('sector')
    specializationidsbysector = InterestSector.objects.filter(personal_interest_sector=sector).values('course_specialization_id')
    if specializationidsbysector is None:
        data.append(sector)
    else:
        for specializationid in specializationidsbysector:
            coursespecialization = CourseSpecialization.objects.filter(course_specialization_id=specializationid['course_specialization_id']).values('course_specialization')
            if len(coursespecialization) is not 0:
                name = coursespecialization[0]['course_specialization']
                if name not in data:
                    data.append(name)
    response['results'] = data
    return HttpResponse(json.dumps(response), content_type="application/json")