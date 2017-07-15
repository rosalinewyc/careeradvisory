from django.db import models

class Job(models.Model):
    job_id = models.IntegerField(primary_key=True)
    job_description = models.CharField(max_length=250)
    job_url = models.CharField(max_length=100)
    job_category=models.CharField(max_length=100)


class Mbti(models.Model):
    mbti_code = models.CharField(max_length=4,primary_key=True)
    mbti_description= models.CharField(max_length=250)
    possible_job_sector = models.CharField(max_length=100)


class Course(models.Model):
    course_code = models.IntegerField(primary_key=True)
    course_name = models.CharField(max_length=128)
    no_of_modules = models.IntegerField()


class Module(models.Model):
    module_code = models.IntegerField(primary_key=True)
    module_name = models.CharField(max_length=128)
    mod_description = models.CharField(max_length=128)
    school = models.CharField(max_length=128)
    has_prerequiste = models.BooleanField(default = True)
    is_elective = models.BooleanField(default = True)


class Prerequisite(models.Model):
    module_code = models.ForeignKey(Module,on_delete=models.CASCADE)
    prereq = models.ForeignKey(Module,related_name="prereq",on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_code', 'prereq')


class User(models.Model):
    user_id = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=128)
    role = models.IntegerField()


class Student(models.Model):
    user_id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    course_code = models.ForeignKey(Course,on_delete=models.CASCADE)
    mbti_code= models.ForeignKey(Mbti,on_delete=models.CASCADE,null=True)
    email = models.CharField(max_length=128)
    profile_picture = models.FileField(null=True)


class InterestSector(models.Model):
    personal_interest_sector = models.CharField(max_length=200)


class StudentInterestSector(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    personal_interest_sector = models.CharField(max_length=200)


class UserElective(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    module_code = models.ForeignKey(Module,on_delete=models.CASCADE)

    class Meta:
        unique_together = ('module_code', 'user_id')


class Counselor(models.Model):
    user_id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    profile_picture = models.FileField(null=True)
    contact_no= models.CharField(max_length=10)

