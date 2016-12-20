from django.db import models

class Question(models.Model):
	# create a table in the database to store questions and corresponding answer
	subject = models.CharField(max_length=100, default='EE147')
	problem = models.TextField()
	figure = models.CharField(max_length=100, default='none')
	answer = models.CharField(max_length=100)
	date = models.DateTimeField()

	def __str__(self):
		return str(self.pk)



class Student(models.Model):
	# create table for student records
	name = models.CharField(max_length=100)
	school_id = models.CharField(max_length=100)
	subject = models.CharField(max_length=100, default='EE147')
	accuracy = models.FloatField()
	def __str__(self):
		return str(self.school_id)


class Response(models.Model):
	# create a table in the database to store the exam sets and answers of the students
	student = models.ForeignKey(Student)
	question = models.ForeignKey(Question)
	answer = models.CharField(max_length=100)
	attempt = models.IntegerField()
	is_correct = models.BooleanField(default=False)
	is_last = models.BooleanField(default=False)
	date = models.DateTimeField()

	def __str__(self):
		return str(self.student)

# class Grades(models.Model):
# 	# create table for student grades
# 	student = models.ForeignKey(Student)
# 	subject = models.CharField(max_length=100, default='EE147')
# 	total_attempts = models.IntegerField()
# 	total_score = models.FloatField()
# 	final_grade = models.FloatField()
# 	updated = models.DateTimeField()
