from django.db import models


class Course(models.Model):
    course_code = models.CharField(max_length=6, primary_key=True)
    course_name = models.CharField(max_length=128)
    no_of_modules = models.IntegerField()


class CourseSpecialization(models.Model):
    course_specialization_id = models.CharField(max_length=10, primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_specialization = models.CharField(max_length=128)


class Module(models.Model):
    module_code = models.IntegerField(primary_key=True)
    module_name = models.CharField(max_length=128)
    school = models.CharField(max_length=128)
    has_prerequiste = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=True)
    specialisation = models.CharField(max_length=128)
    mod_description = models.TextField()


class Prerequisite(models.Model):
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE)
    prereq = models.ForeignKey(Module, related_name="prereq", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_code', 'prereq')


class CourseMapping(models.Model):
    course_mapping_id = models.IntegerField(primary_key=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField()


class JobCategory(models.Model):
    job_category_id = models.IntegerField(primary_key=True)
    job_category = models.CharField(max_length=200)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)


class InterestSector(models.Model):
    interest_sector_id = models.IntegerField(primary_key=True)
    personal_interest_sector = models.CharField(max_length=200)


class Job(models.Model):
    job_id = models.CharField(max_length=255, primary_key=True)
    job_url = models.TextField(null=True)
    job_position = models.TextField(null=True)
    job_company = models.TextField(null=True)
    job_category = models.TextField(null=True)
    job_description = models.TextField(null=True)
    job_date = models.DateField()
    job_keyword = models.CharField(max_length=255, null=True)
    job_interest = models.CharField(max_length=255, null=True)


class Mbti(models.Model):
    mbti_code = models.CharField(max_length=4,primary_key=True)
    mbti_description= models.TextField()
    possible_job_sector = models.TextField()


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=128)
    role = models.IntegerField()


class Student(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=128)
    mbti_code = models.ForeignKey(Mbti, on_delete=models.CASCADE, null=True)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_specialization = models.CharField(max_length=128, null=True)
    current_year = models.IntegerField()
    current_semester = models.IntegerField()
    email = models.CharField(max_length=128)
    profile_picture = models.FileField(null=True)


class StudentInterestSector(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    personal_interest_sector = models.ForeignKey(InterestSector, on_delete=models.CASCADE)


class ModuleCompleted(models.Model):
    user_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_code', 'user_id')


class UserElective(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    module_code = models.ForeignKey(Module, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_code', 'user_id')


class Counselor(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.FileField(null=True)
    contact_no = models.CharField(max_length=10)
