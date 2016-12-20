from django.conf.urls import url, include
from . import views
from django.views.generic import ListView, DetailView
from exams.models import Question, Student, Response

urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^home/$', views.home, name='home'),
    url(r'^exams/$', views.question, name='question'),
    url(r'^evaluate/$', views.evaluate, name='evaluate'),
    url(r'^summary/$', views.summary_login, name='summary'),
    url(r'^results/$', views.results, name='results'),
    url(r'^$', ListView.as_view(queryset=Question.objects.all().order_by("-date")[:25],
        template_name="exams/exams_admin.html")),
    url(r'^$', ListView.as_view(queryset=Student.objects.all().order_by("-name")[:25],
        template_name="exams/exams_admin.html")),
    url(r'^$', DetailView.as_view(queryset=Response.objects.all().order_by("-student")[:25],
        template_name="exams/exams_admin.html")),
    ]
