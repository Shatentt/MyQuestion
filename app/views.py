from django.contrib import auth
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from app.forms import AnswerForm, LoginForm, QuestionForm, RegisterForm, SettingsForm
from app.models import Question, Like, Tag

def paginate(request, objects, per_page=5):
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(objects, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    questions = Question.objects.new()

    page = paginate(request, questions)

    return render(request, 'index.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })

def hot_questions(request):
    questions = Question.objects.popular()

    page = paginate(request, questions)

    return render(request, 'hot_questions.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })

@login_required(login_url='login')
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return redirect(question) 
    else:
        form = QuestionForm()

    return render(request, 'ask.html', {'form': form})

def question(request, pk):
    question = Question.objects.get_with_answers(pk)
    answers = answers = getattr(question, 'answers_ordered', [])
    answers_cnt = getattr(question, 'answers_cnt', len(answers))
    page = paginate(request, answers)
    
    return render(request, 'question.html', context={
        'answers_cnt': answers_cnt,
        'question': question,
        'answers': page.object_list,
        'page_obj': page,
    })

def tag(request, pk):
    tag_item = Tag.objects.get_by_id(pk)

    if tag_item is None:
        raise Http404("Tag does not exist")

    questions = Question.objects.tagged(tag_item)

    page = paginate(request, questions)

    return render(request, 'tag.html', context={
        'questions': page.object_list,
        'page_obj': page,
        'tag': tag_item,
    })

def settings(request):
    return render(request, 'settings.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
        
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    next_url = request.GET.get('next') or request.POST.get('next') or reverse('index')

    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return HttpResponseRedirect(next_url)
    else:
        form = LoginForm()
        
    return render(request, 'login.html', context={'form': form, 'next': next_url})
    

def logout(request):
    auth.logout(request)
    
    next_page = request.GET.get('next')
    
    if next_page:
        return HttpResponseRedirect(next_page)
    
    return HttpResponseRedirect(reverse('index'))

def question(request, pk):
    q = Question.objects.get_with_answers(pk)
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = q
                
                answer.user = request.user.profile 
                
                answer.save()
                
                return redirect('question', pk=q.id)
        else:
            return redirect('login')
    else:
        form = AnswerForm()

    answers = getattr(q, 'answers_ordered', [])
    answers_cnt = getattr(q, 'answers_cnt', len(answers))
    page = paginate(request, answers)

    print(answers_cnt)
    
    return render(request, 'question.html', context={
        'answers_cnt': answers_cnt,
        'question': q,
        'answers': page.object_list,
        'page_obj': page,
        'form': form,
    })

@login_required
def settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('settings')
    else:
        form = SettingsForm(instance=request.user)
    
    return render(request, 'settings.html', {'form': form})

# @login_required
# @require_POST
# def like_toggle(request):
#     user = request.user
#     data = request.POST

#     content_type_id = data.get('content_type_id')
#     if content_type_id:
#         try:
#             ct = ContentType.objects.get_for_id(int(content_type_id))
#         except Exception:
#             return JsonResponse({'error': 'invalid content_type_id'}, status=400)
#     else:
#         ct_name = data.get('content_type')
#         if not ct_name:
#             return JsonResponse({'error': 'content_type is required'}, status=400)
#         try:
#             app_label, model = ct_name.split('.')
#             ct = ContentType.objects.get(app_label=app_label, model=model.lower())
#         except Exception:
#             return JsonResponse({'error': 'invalid content_type'}, status=400)

#     try:
#         object_id = int(data.get('object_id'))
#     except (TypeError, ValueError):
#         return JsonResponse({'error': 'invalid object_id'}, status=400)

#     like_qs = Like.objects.filter(user=user, content_type=ct, object_id=object_id)
#     if like_qs.exists():
#         like_qs.delete()
#         liked = False
#     else:
#         Like.objects.create(user=user, content_type=ct, object_id=object_id)
#         liked = True

#     count = Like.objects.filter(content_type=ct, object_id=object_id).count()

#     return JsonResponse({'liked': liked, 'count': count})