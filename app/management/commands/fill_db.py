import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.hashers import make_password
from app.models import Profile, Tag, Question, Answer, Like

def rnd_text(words=10):
    return ' '.join(''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
                    for _ in range(words))

class Command(BaseCommand):
    help = 'Fill DB with test data: python manage.py fill_db [ratio]'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio <= 0:
            self.stderr.write('ratio должен быть > 0')
            return

        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_likes = ratio * 200

        self.stdout.write('Начинаем генерацию данных...')

        default_password = make_password('password') 
        
        last_id = User.objects.last().id if User.objects.exists() else 0
        
        users_list = [
            User(
                username=f'testuser_{last_id + i + 1}',
                email=f'testuser_{last_id + i + 1}@example.com',
                password=default_password,
                is_active=True
            ) for i in range(num_users)
        ]

        User.objects.bulk_create(users_list, ignore_conflicts=True)
        
        users = list(User.objects.filter(username__startswith='testuser_').order_by('-id')[:num_users])

        self.stdout.write(f'Создано пользователей: {len(users)}')

        existing_profile_user_ids = set(Profile.objects.values_list('user_id', flat=True))
        profiles_list = [
            Profile(user=u) 
            for u in users 
            if u.id not in existing_profile_user_ids
        ]
        Profile.objects.bulk_create(profiles_list, ignore_conflicts=True)
        
        profiles = list(Profile.objects.filter(user__in=users))
        self.stdout.write(f'Создано профилей: {len(profiles_list)}')

        last_tag_id = Tag.objects.last().id if Tag.objects.exists() else 0
        tags_list = [
            Tag(name=f'tag_{last_tag_id + i + 1}_{rnd_text(1)}') 
            for i in range(num_tags)
        ]
        Tag.objects.bulk_create(tags_list, ignore_conflicts=True)
        
        tags = list(Tag.objects.all().order_by('-id')[:num_tags])
        self.stdout.write(f'Создано тегов: {len(tags)}')

        questions_list = [
            Question(
                title=f'Question {i+1} {rnd_text(3)}',
                text=rnd_text(40),
                user=random.choice(users)
            ) for i in range(num_questions)
        ]
        Question.objects.bulk_create(questions_list)
        
        questions = list(Question.objects.all().order_by('-created_at')[:num_questions])
        self.stdout.write(f'Создано вопросов: {len(questions)}')

        QuestionTag = Question.tags.through
        q_tags_relations = []
        for q in questions:
            if not tags: break
            cnt = random.randint(1, min(3, len(tags)))
            chosen_tags = random.sample(tags, k=cnt)
            for t in chosen_tags:
                q_tags_relations.append(QuestionTag(question_id=q.id, tag_id=t.id))
        
        QuestionTag.objects.bulk_create(q_tags_relations, ignore_conflicts=True)
        self.stdout.write('Теги привязаны к вопросам')

        answers_list = [
            Answer(
                question=random.choice(questions),
                text=rnd_text(20),
                user=random.choice(profiles),
                is_correct=(random.random() < 0.05)
            ) for _ in range(num_answers)
        ]
        Answer.objects.bulk_create(answers_list)
        
        answers = list(Answer.objects.all().order_by('-created_at')[:num_answers])
        self.stdout.write(f'Создано ответов: {len(answers)}')
        
        all_targets = questions + answers
        ct_question = ContentType.objects.get_for_model(Question)
        ct_answer = ContentType.objects.get_for_model(Answer)
        
        likes_to_create = []
        unique_likes = set()
        
        attempts = 0
        max_attempts = num_likes * 5
        
        while len(likes_to_create) < num_likes and attempts < max_attempts:
            attempts += 1
            target = random.choice(all_targets)
            prof = random.choice(profiles)
            
            if isinstance(target, Question):
                ct_id = ct_question.id
            else:
                ct_id = ct_answer.id
                
            pair = (prof.id, ct_id, target.id)
            
            if pair in unique_likes:
                continue
            
            unique_likes.add(pair)
            likes_to_create.append(
                Like(user=prof, content_type_id=ct_id, object_id=target.id)
            )

        Like.objects.bulk_create(likes_to_create, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(
            f'Успешно! Создано лайков: {len(likes_to_create)} (цель: {num_likes})'
        ))