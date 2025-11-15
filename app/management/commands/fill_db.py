import random
import string

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

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

        users = []
        for i in range(num_users):
            username = f'testuser_{i+1}'
            u, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                u.set_password('password')
                u.save()
            Profile.objects.get_or_create(user=u)
            users.append(u)

        tags = []
        for i in range(num_tags):
            t, _ = Tag.objects.get_or_create(name=f'tag_{i+1}')
            tags.append(t)

        questions = []
        for i in range(num_questions):
            u = random.choice(users)
            q = Question.objects.create(
                title=f'Question {i+1} {rnd_text(3)}',
                text=rnd_text(40),
                user=u
            )
            if tags:
                q.tags.add(*random.sample(tags, k=random.randint(1, min(3, len(tags)))))
            questions.append(q)

        profiles = [p for p in Profile.objects.filter(user__in=users)]
        answers = []
        for i in range(num_answers):
            a = Answer.objects.create(
                question=random.choice(questions),
                text=rnd_text(20),
                user=random.choice(profiles),
                is_correct=(random.random() < 0.05)
            )
            answers.append(a)

        all_targets = questions + answers
        created_likes = 0
        attempts = 0
        max_attempts = max(1000, num_likes * 10)  # защита от бесконечного цикла

        while created_likes < num_likes and attempts < max_attempts:
            attempts += 1
            target = random.choice(all_targets)
            ct = ContentType.objects.get_for_model(target.__class__)
            prof = random.choice(profiles)

            exists = Like.objects.filter(user=prof, content_type=ct, object_id=target.pk).exists()
            if exists:
                continue

            Like.objects.create(user=prof, content_type=ct, object_id=target.pk)
            created_likes += 1

        if created_likes < num_likes:
            self.stdout.write(self.style.WARNING(
                f'Достигнут лимит попыток {max_attempts}, много дубликатов.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'Создано лайков: {created_likes}'))

        self.stdout.write(f'Created: users={len(users)}, tags={len(tags)}, questions={len(questions)}, answers={len(answers)}, likes={num_likes}')
