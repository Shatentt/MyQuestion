import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_project.settings")
django.setup()

from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer

fake = Faker()

NUM_USERS = 5
NUM_TAGS = 8
NUM_QUESTIONS = 30
ANSWERS_PER_QUESTION = 6

def run():
    users = []
    for i in range(NUM_USERS):
        username = f"user{i}_{fake.user_name()}"
        user, created = User.objects.get_or_create(username=username, defaults={"email": fake.email()})
        if created:
            user.set_password("password123")
            user.save()
        profile, _ = Profile.objects.get_or_create(user=user)
        users.append((user, profile))

    tags = []
    for i in range(NUM_TAGS):
        tname = f"{fake.word()}_{i}"
        tag, _ = Tag.objects.get_or_create(name=tname)
        tags.append(tag)

    for i in range(NUM_QUESTIONS):
        title = fake.sentence(nb_words=6)
        text = fake.paragraph(nb_sentences=3)
        user, profile = random.choice(users)
        q = Question.objects.create(title=title, text=text, user=user)
        q.tags.set(random.sample(tags, k=random.randint(0, min(3, len(tags)))))
        for j in range(ANSWERS_PER_QUESTION):
            Answer.objects.create(question=q, text=fake.paragraph(), is_correct=(j==0), user=profile)

if __name__ == "__main__":
    run()
    print("Done.")
