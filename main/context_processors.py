from .models import Message

def unread_counts(request):
    if not request.user.is_authenticated:
        return {
            'unread_message_count': 0,
            'unread_notification_count': 0,
        }
    
    unread_message_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    unread_notification_count = request.user.notifications.filter(is_read=False).count()

    return {
        'unread_message_count': unread_message_count,
        'unread_notification_count': unread_notification_count,
    }
