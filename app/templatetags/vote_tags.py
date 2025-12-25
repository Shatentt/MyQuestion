from django import template
from app.models import Like

register = template.Library()

@register.simple_tag
def get_user_vote(obj, user):
    """
    Принимает объект (вопрос/ответ) и пользователя (request.user).
    Возвращает 1, -1 или 0.
    """
    if not user.is_authenticated:
        return 0
    
    try:
        profile = user.profile
    except:
        return 0

    like = obj.likes.filter(user=profile).first()
    
    if like:
        return like.vote
    return 0