from django.db import models


class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    course_name = models.CharField(max_length=128, null=False)
    no_of_modules = models.IntegerField(null=True)


class CourseSpecialization(models.Model):
    course_specialization_id = models.CharField(max_length=10, primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    course_specialization = models.CharField(max_length=128, null=False)


class Module(models.Model):
    module_code = models.IntegerField(primary_key=True)
    module_name = models.CharField(max_length=128, null=False)
    school = models.CharField(max_length=128, null=False)
    has_prerequiste = models.BooleanField(default=True)
    mod_description = models.TextField(null=True)


class SpecializationModule(models.Model):
    specialization_module_id = models.IntegerField(primary_key=True)
    course_specialization_id = models.ForeignKey(CourseSpecialization, on_delete=models.CASCADE, null=False)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)


class Prerequisite(models.Model):
    prerequisite_id = models.IntegerField(primary_key=True)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)
    prereq = models.ForeignKey(Module, related_name="prereq", on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('module_code', 'prereq')


class CourseMapping(models.Model):
    course_mapping_id = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)
    year = models.IntegerField(null=False)
    semester = models.IntegerField(null=False)


class JobCategory(models.Model):
    job_category_id = models.IntegerField(primary_key=True)
    job_category = models.CharField(max_length=200, null=False)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)


class InterestSector(models.Model):
    interest_sector_id = models.IntegerField(primary_key=True)
    personal_interest_sector = models.CharField(max_length=200, null=False)
    course_specialization_id = models.ForeignKey(CourseSpecialization, on_delete=models.CASCADE, null=True)


class Job(models.Model):
    job_id = models.CharField(max_length=255, primary_key=True)
    job_url = models.TextField(null=True)
    job_position = models.TextField(null=True)
    job_company = models.TextField(null=True)
    job_category = models.TextField(null=True)
    job_description = models.TextField(null=True)
    job_date = models.DateField(null=False)
    job_keyword = models.CharField(max_length=255, null=True)
    job_interest = models.CharField(max_length=255, null=True)
    job_mbti = models.CharField(max_length=255, null=True)


class Mbti(models.Model):
    mbti_code = models.CharField(max_length=4, primary_key=True)
    mbti_description = models.TextField()
    possible_job_sector = models.TextField()


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=128, null=False)
    role = models.IntegerField(null=False)


# added capstone & Internship
class Student(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=128, null=False)
    mbti_code = models.ForeignKey(Mbti, on_delete=models.CASCADE, null=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    current_year = models.IntegerField(null=False)
    current_semester = models.IntegerField(null=False)
    email = models.CharField(max_length=128, null=False)
    profile_picture = models.FileField(null=True)
    course_specialization = models.ForeignKey(CourseSpecialization, on_delete=models.CASCADE, null=True)
    choose_capstone = models.BooleanField(default=True)
    choose_internship = models.BooleanField(default=True)


class StudentInterestSector(models.Model):
    #studentInterestSector_id = models.CharField(max_length=4, primary_key=True)
    studentInterestSector_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    personal_interest_sector = models.ForeignKey(InterestSector, on_delete=models.CASCADE, null=False)


class ModuleCompleted(models.Model):
    modulecompleted = models.CharField(max_length=4, primary_key=True)
    user_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=False)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('module_code', 'user_id')


class UserElective(models.Model):
    userElective_id = models.CharField(max_length=4, primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)

    class Meta:
        unique_together = ('module_code', 'user_id')


class Counselor(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.FileField(null=True)
    contact_no = models.CharField(max_length=10, null=False)


class ElectiveModule(models.Model):
    elective_code = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE, null=False)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)


class StudentChosenModule(models.Model):
    student_chosen_module_id = models.AutoField(primary_key=True)
    position = models.IntegerField(null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    student_module_interest = models.ForeignKey(Module, on_delete=models.CASCADE, null=False)


class JobAnalytics(models.Model):
    job_title = models.CharField(max_length=128, null=False)
    sector_type = models.CharField(max_length=128, null=False)
    clicks = models.IntegerField(null=True)


class BookmarkJob(models.Model):
    bm_job_id = models.AutoField(max_length=255, primary_key=True)
    job_id = models.TextField(max_length=255, null=False)
    job_url = models.TextField(null=True)
    job_position = models.TextField(null=True)
    job_company = models.TextField(null=True)
    job_category = models.TextField(null=True)
    job_description = models.TextField(null=True)
    job_date = models.DateField(null=False)
    job_keyword = models.CharField(max_length=255, null=True)
    job_interest = models.CharField(max_length=255, null=True)
    job_mbti = models.CharField(max_length=255, null=True)