from .models import Notification


def notification_count(request):
    """
    Context processor to add unread notification count to all templates
    """
    if request.user.is_authenticated and (request.user.role in ["COMPANY_ADMIN", "MANAGER"]):
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

        return {"unread_notification_count": unread_count}

    return {"unread_notification_count": 0}
