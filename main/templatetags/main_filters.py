from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter
def time_ago(value):
    now = timezone.now()
    diff = now - value

    if diff.days > 365:
        return f'{diff.days // 365}년 전'
    elif diff.days > 30:
        return f'{diff.days // 30}개월 전'
    elif diff.days > 7:
        return f'{diff.days // 7}주 전'
    elif diff.days > 0:
        return f'{diff.days}일 전'
    elif diff.seconds > 3600:
        return f'{diff.seconds // 3600}시간 전'
    elif diff.seconds > 60:
        return f'{diff.seconds // 60}분 전'
    else:
        return f'방금 전'
