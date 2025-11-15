from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from app.models import Question, Like

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

def ask(request):
    return render(request, 'ask.html')

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
    questions = Question.objects.tagged(pk)

    page = paginate(request, questions)

    return render(request, 'tag.html', context={
        'questions': page.object_list,
        'page_obj': page,
    })

def settings(request):
    return render(request, 'settings.html')

def register(request):
    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')

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