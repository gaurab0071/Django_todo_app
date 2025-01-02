from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Reminder

@shared_task
def send_reminders():
    reminders = Reminder.objects.filter(reminder_time__lte=timezone.now())
    for reminder in reminders:
        send_mail(
            'Reminder Notification',
            f'This is a reminder for your task: {reminder.todo.todo_name}',
            'bhttraigaurab332@gmail.com',
            [reminder.todo.user.email],
            fail_silently=False,
        )
        reminder.is_sent = True
        reminder.save() # Remove after sending


