from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.urls import reverse
from django.db import models
from django.db.models import Count, Prefetch
from django.apps import apps

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    avatar = models.ImageField(default='static/images/silly cat.jpg', upload_to=['profile_pics'])

    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class QuestionQuerySet(models.QuerySet):
    def new(self):
        return self.order_by('-created_at')

    def popular(self):
        return self.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')

    def tagged(self, tag):
        if isinstance(tag, Tag):
            return self.filter(tags=tag)
        if isinstance(tag, int):
            return self.filter(tags__id=tag)
        return self.filter(tags__name=str(tag))
    
    def with_answers(self):
        Answer = apps.get_model('app', 'Answer')
        return self.prefetch_related(
            Prefetch('answer_set', queryset=Answer.objects.order_by('created_at'), to_attr='answers_ordered')
        )
    
    def with_answers_count(self):
        return self.annotate(answers_cnt=Count('answer'))

    def get_with_answers(self, pk):
        return self.with_answers().with_answers_count().get(pk=pk)



class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def new(self):
        return self.get_queryset().new()

    def popular(self):
        return self.get_queryset().popular()

    def tagged(self, tag):
        return self.get_queryset().tagged(tag)
    
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)
    
    def get_with_answers(self, pk):
        return self.get_queryset().get_with_answers(pk)

class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation('app.Like', related_query_name='question')

    objects = QuestionManager()

    def __str__(self):
        return self.title
    
    def like_count(self):
        return getattr(self, 'like_count', self.likes.count())

    def answer_count(self):
        return getattr(self, 'answer_count', self.answer_set.count())

    def full_url(self, request):
        return request.build_absolute_uri(self.get_absolute_url())
    
    def get_absolute_url(self):
        return reverse('question', args=[str(self.pk)])

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False, blank=True, null=True)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = GenericRelation('app.Like', related_query_name='answer')

    def __str__(self):
        return self.text[:50]

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'content_type', 'object_id'), name='unique_user_like')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"By {self.user} for {self.content_type}({self.object_id})"