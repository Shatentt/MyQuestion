from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def hot_questions(request):
    return render(request, 'hot_questions.html')

def ask(request):
    return render(request, 'ask.html')

def question(request):
    return render(request, 'question.html')