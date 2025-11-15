from django.contrib import admin
from app.models import Tag, Question, Answer, Profile, Like

admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Profile)
admin.site.register(Like)