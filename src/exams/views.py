from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .forms import loginForm, responseForm, hiddenForm
from .models import Question, Student, Response
from django.views.generic import ListView, DetailView
import random as rn
import numpy as np


# global variables
global q_goal
q_goal = 10


def login(request):
    link = 'exams/login.html'
    title = ''
    instruction = 'Please enter your ID number.'
    formLogin = loginForm
    status = 'logged-out'
    context = {
        'title': title,
        'instruction': instruction,
        'formLogin': formLogin,
        'status': status,
    }
    return render(request, link, context)


def home(request):
    user_id = request.POST['ID']
    print(user_id)
    try:
        student = Student.objects.get(school_id=user_id)
        # retrieve existing questions and responses
        existing_responses = Response.objects.all().filter(student_id=student)
        n_existing_responses = len(existing_responses)
        print(n_existing_responses)        

        if n_existing_responses > 0:
            
            unfinished = existing_responses.filter(is_correct=False, is_last=True)
          
            if len(unfinished) > 0:
                formHidden = hiddenForm(initial={'ID': user_id, 'response_key': int(unfinished[0].pk)})

                # calculate performance so far
                latest_responses = Response.objects.all().filter(student_id=student, is_last=True)
                correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True) 
                total_correct = len(correct_responses)
                total_trials = 0
                for r in latest_responses:
                    total_trials += int(r.attempt)
                score = total_correct/total_trials
                performance = 'Commulative accuracy: ' + str(100*score) + ' %' +  ' out of ' + str(total_trials)+ ' attempts.'


                n_unfinished = len(unfinished)
                status = 'logged-in'
                link = 'exams/home.html'
                title = 'Welcome back!'
                instruction = 'You have ' + str(n_unfinished) + ' unsolved problems. Please click proceed to continue solving your sets of problems. Good luck.'
                context = { 
                    "title": title,
                    "instruction": instruction,
                    "status": status,
                    "formHidden": formHidden,
                    "performance": performance
                }
            else:
                link = 'exams/finished.html'
                title = 'Finished!'
                instruction = 'You have finished solving the required problems.'
                status = 'logged-in'
                instruction2 = 'Would you like to solve another problem?'
                caution = 'Caution: Solving another problem may increase or decrease your overall rating.'
                
                # calculate performance so far
                latest_responses = Response.objects.all().filter(student_id=student, is_last=True)
                correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True) 
                total_correct = len(correct_responses)
                total_trials = 0
                for r in latest_responses:
                    total_trials += int(r.attempt)
                score = total_correct/total_trials
                performance = 'Commulative accuracy: ' + str(100*score) + ' %' +  ' out of ' + str(total_trials)+ ' attempts.'

                # get other questions if the user decides to solve another question
                solved_questions_pk = [r.question.pk for r in latest_responses]
                unsolved_questions_pk = Question.objects.all().exclude(pk__in=solved_questions_pk)
                print(unsolved_questions_pk)
                formHidden = hiddenForm(initial={'ID': user_id, 'response_key': unsolved_questions_pk[0]})
                
                context = { 
                    "title": title,
                    "instruction": instruction,
                    "status": status,
                    'performance': performance,
                    "formHidden": formHidden,
                    "instruction2": instruction2,
                    "caution": caution
                }

        else:  # select random questions (first time login initialize response)
            all_question = np.arange(1, Question.objects.count()+1, 1, dtype = int)
            q_selection = rn.sample(list(all_question), q_goal)
            questions = Question.objects.all().filter(pk__in=q_selection)
            print([q.pk for q in questions])
            for q in questions:
                Response.objects.create(student=student, question=q, answer=0, attempt=0, is_correct=False, is_last=True, date=timezone.localtime(timezone.now()))
            
            unfinished = existing_responses.filter(student_id=student, is_correct=False, is_last=True)
            formHidden = hiddenForm(initial={'ID': user_id, 'response_key': int(unfinished[0].pk)})
   
            status = 'logged-in'
            link = 'exams/home.html'
            title = 'You are logged in.'
            instruction = 'The system has randomly selected problems for you to solve. Please click proceed to start. Good luck.'
            caution = ''
            context = {
                "title": title,
                "instruction": instruction,
                "status": status,
                "formHidden": formHidden,
                "caution": caution
            }
    except:
        link = 'exams/login.html'
        title = 'Error!'
        instruction = 'The ID you have entered is not in the database. Please enter a valid ID number.'
        formLogin = loginForm
        status = 'logged-out'
        context = {
            "title": title,
            "instruction": instruction,
            "formLogin": formLogin,
            "status": status,
        }

        
    return render(request, link, context)




def question(request):
    user_id = request.POST['ID']
    student = Student.objects.get(school_id=user_id)
    # retrieve existing questions and responses
    unfinished = Response.objects.all().filter(student_id=student, is_correct=False, is_last=True)
    
    # this block will be performed when the user wishes to answer more questions on top of the required questions
    if len(unfinished) == 0:
        new_question_pk = request.POST['response_key']
        q = Question.objects.get(pk=new_question_pk)
        Response.objects.create(student=student, question=q, answer=0, attempt=0, is_correct=False, is_last=True, date=timezone.localtime(timezone.now()))
        unfinished = Response.objects.all().filter(student_id=student, is_correct=False, is_last=True)        
    
    question = unfinished[0].question
    problem = question.problem


    formHidden = hiddenForm(initial={'ID': user_id, 'response_key': int(unfinished[0].pk)})

    link = 'exams/question.html'
    title = 'Question:'
    instruction = problem
    formResponse = responseForm
    status = 'logged-in'
    context = {
        'title': title,
        'instruction': instruction,
        'formResponse': formResponse,
        'status': status,
        "formHidden": formHidden
    }

    return render(request, link, context)


def evaluate(request):
    link = 'exams/evaluate.html'
    status = 'logged-in'
    
    user_id = request.POST['ID']
    response_key = int(request.POST['response_key'])
    student = Student.objects.get(school_id=user_id)
    response = Response.objects.get(pk=response_key)
    formHidden = hiddenForm(initial={'ID': user_id, 'response_key': int(response_key)})
        
    user_answer = float(request.POST['response'])
    correct_answer = float(response.question.answer)
    # print(correct_answer)
    print('answer:', correct_answer*1.01, correct_answer*0.99, user_answer)

    if (correct_answer*0.97) < user_answer < (correct_answer*1.03):
        # create a new response
        Response.objects.create(student=student, question=response.question, answer=user_answer, attempt=response.attempt+1, is_correct=True, is_last=True, date=timezone.localtime(timezone.now()))
        
        # update the previous response
        response.is_last = False
        response.save()

        # calculate performance so far
        latest_responses = Response.objects.all().filter(student_id=student, is_last=True)
        correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True)
         
        total_correct = len(correct_responses)
        total_trials = 0
        for r in latest_responses:
            total_trials += int(r.attempt)
        score = total_correct/total_trials


        title = 'Good job!'
        instruction = 'Your answer is correct.'
        performance = 'Commulative accuracy: ' + str(100*score) + ' %' +  ' out of ' + str(total_trials)+ ' attempts.'

        # check if there are unfinished problems
        unfinished = Response.objects.all().filter(student_id=student, is_correct=False, is_last=True)
        if len(unfinished) > 0:
            instruction = instruction + ' Problems left: '+ str(len(unfinished))  
            instruction2 = ''
            caution = ' '
        else:
            link = 'exams/finished.html'
            title = 'Congratulations!'
            instruction = 'You have finished solving the required problems.'
            # formResponse = responseForm
            formHidden = hiddenForm(initial={'ID': user_id, 'response_key': int(response_key)})
            instruction2 = 'Would you like to solve another problem?'           
            caution = 'Caution: Solving another problem may increase or decrease your overall rating.'
            # get other questions if the user decides to solve another question
            solved_questions_pk = [r.question.pk for r in latest_responses]
            unsolved_questions_pk = Question.objects.all().exclude(pk__in=solved_questions_pk)
            print(unsolved_questions_pk)
            formHidden = hiddenForm(initial={'ID': user_id, 'response_key': unsolved_questions_pk[0]})
                

    else:
        # create a new response
        Response.objects.create(student=student, question=response.question, answer=user_answer, attempt=response.attempt+1, is_correct=False, is_last=True, date=timezone.localtime(timezone.now()))
        
        # update the data of the previous response
        response.is_last = False
        response.save()

        # calculate performance so far
        latest_responses = Response.objects.all().filter(student_id=student, is_last=True)
        correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True)
         
        total_correct = len(correct_responses)
        total_trials = 0
        for r in latest_responses:
            total_trials += int(r.attempt)
        score = total_correct/total_trials

        title = 'Oopps!'
        instruction = 'Your answer is beyond the tolerable range. Please recheck your solution and rounding-off of the numerical values.'
        performance = 'Performance accuracy: ' + str(100*score) + ' %' +  ' out of ' + str(total_trials)+ ' attempts.'
        instruction2 = ''
        caution = ''

    context = {
    'title': title,
    'instruction': instruction,
    'formHidden': formHidden,
    'status': status,
    'instruction2': instruction2,
    'caution': caution,
    'performance': performance
    }
    return render(request, link, context)


def summary_login(request):
    link = 'exams/summary_login.html'
    title = ''
    instruction = 'Please enter the ID number.'
    formLogin = loginForm


    # get all performances of all students
    all_students = Student.objects.all()    
    for student in all_students:
        latest_responses = Response.objects.all().filter(student_id=student, is_last=True)
        correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True)
        total_correct = len(correct_responses)        
        
        # get total trials
        total_trials = 0
        for r in latest_responses:
            total_trials += int(r.attempt)
        # calculate scores
        if total_trials > 0:
            score = total_correct/total_trials
            if total_correct < 10 or score < 0.5: 
                final_grade = 'INC'
            elif 0.50 <= score < 0.55:
                final_grade = '3.00'
            elif 0.55 <= score < 0.60:
                final_grade = '2.75'
            elif 0.60 <= score < 0.65:
                final_grade = '2.50'
            elif 0.65 <= score < 0.70:
                final_grade = '2.25'
            elif 0.70 <= score < 0.75:
                final_grade = '2.00'
            elif 0.75 <= score < 0.80:
                final_grade = '1.75'
            elif 0.80 <= score < 0.90:
                final_grade = '1.50'
            elif 0.90 <= score < 1.00:
                final_grade = '1.25'
            elif score == 1.00:
                final_grade = '1.00'
            else:
                final_grade = 'INC'
        else:
            score = 0
            final_grade = 'INC'
        
        print(student.school_id, final_grade, student.name, total_correct, total_trials, score)

    status = 'logged-out'
    context = {
        'title': title,
        'instruction': instruction,
        'formLogin': formLogin,
        'status': status,
    }
    return render(request, link, context)

def results(request):
    link = 'exams/results.html'
    student_id = request.POST['ID']
    print(student_id)
    student = Student.objects.get(school_id=student_id)
    responses = Response.objects.all().filter(student_id=student).exclude(answer=0)
    
    list_responses = []
    for r in responses:
        print(r.question.answer, r.answer, r.is_correct)
        list_responses.append([r.question.answer, r.answer, r.is_correct])


    # calculate performance so far
    latest_responses = responses.filter(student_id=student, is_last=True)
    correct_responses = latest_responses.filter(is_correct=True) #Response.objects.all().filter(student_id=student, is_last=True, is_correct=True)
     
    total_correct = len(correct_responses)
    # get total trials
    total_trials = 0
    for r in latest_responses:
        total_trials += int(r.attempt)
    # calculate scores
    if total_trials > 0:
        score = total_correct/total_trials
        if total_correct < 10 or score < 0.5: 
            final_grade = 'INC'
        elif 0.50 <= score < 0.55:
            final_grade = '3.00'
        elif 0.55 <= score < 0.60:
            final_grade = '2.75'
        elif 0.60 <= score < 0.65:
            final_grade = '2.50'
        elif 0.65 <= score < 0.70:
            final_grade = '2.25'
        elif 0.70 <= score < 0.75:
            final_grade = '2.00'
        elif 0.75 <= score < 0.80:
            final_grade = '1.75'
        elif 0.80 <= score < 0.90:
            final_grade = '1.50'
        elif 0.90 <= score < 1.00:
            final_grade = '1.25'
        elif score == 1.00:
            final_grade = '1.00'
        else:
            final_grade = 'INC'
    else:
        score = 0
        final_grade = 'INC'

    name = 'Name: '+ str(student.name)
    id_number = 'ID: ' + str(student.school_id)
    accuracy = 'Accuracy: '+ str(score)
    grade = 'Grade: ' + str(final_grade)


    title = ''
    instruction = 'Performance summary:'
    # formLogin = loginForm
    status = 'logged-out'
    context = {
        'title': title,
        'instruction': instruction,
        'name': name,
        'id_number': id_number,
        'accuracy': accuracy,
        'grade': grade,
        'status': status,
        # 'list_responses': list_responses,
    }
    return render(request, link, context)


'''
Final Grade scale:
1:      100
1.25:   90
1.5:    80
1.75:   75
2:      70
2.25:   65
2.5:    60
2.75:   55
3:      50

'''