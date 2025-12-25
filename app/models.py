from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.urls import reverse
from django.db import models
from django.db.models import Count, Prefetch
from django.apps import apps
from django.templatetags.static import static
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    @property
    def avatar_url(self):
        if self.avatar:
            try:
                if self.avatar.storage.exists(self.avatar.name):
                    return self.avatar.url
            except Exception:
                pass
        
        return static('images/silly_cat.jpg')
    
class TagManager(models.Manager):
    def get_by_id(self, pk):
        try:
            return self.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def get_by_name(self, name):
        return self.filter(name=name).first()

class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = TagManager()

    def __str__(self):
        return self.name

class QuestionQuerySet(models.QuerySet):
    def new(self):
        return self.with_answers_count().order_by('-created_at')

    def popular(self):
        return self.annotate(rating=Coalesce(Sum('likes__vote'), 0)).annotate(answers_cnt=Count('answer')).order_by('-rating', '-created_at')

    def tagged(self, tag):
        if isinstance(tag, Tag):
            return self.filter(tags=tag)
        if isinstance(tag, int):
            return self.filter(tags__id=tag)
        return self.filter(tags__name=str(tag))
    
    def with_answers(self):
        Answer = apps.get_model('app', 'Answer')
        return self.prefetch_related(
            Prefetch(
                'answer_set', 
                queryset=Answer.objects.annotate(
                    rating=Coalesce(Sum('likes__vote'), 0)
                ).select_related('user').order_by('-rating', '-created_at'),
                to_attr='answers_ordered' # <--- Вот атрибут, который ищет ваша вьюха
            )
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
    
    @property
    def like_count(self):
        if hasattr(self, 'rating'):
            return self.rating
        
        res = self.likes.aggregate(Sum('vote'))
        return res['vote__sum'] or 0

    @property
    def answer_count(self):
        if hasattr(self, 'answers_cnt'):
            return self.answers_cnt
        return self.answer_set.count()

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

    @property
    def like_count(self):
        if hasattr(self, 'rating'):
            return self.rating
        return self.likes.aggregate(Sum('vote'))['vote__sum'] or 0

    def __str__(self):
        return self.text[:50]

class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='likes')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    LIKE = 1
    DISLIKE = -1
    VOTE_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    )

    vote = models.SmallIntegerField(choices=VOTE_CHOICES, verbose_name="Vote")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('user', 'content_type', 'object_id'), name='unique_user_like')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"By {self.user} for {self.content_type}({self.object_id})"