from django.contrib import admin
from exams.models import Question, Response, Student

admin.site.register(Question)
admin.site.register(Response)
admin.site.register(Student)