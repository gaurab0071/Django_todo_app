from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from todoapp.models import Reminder

@shared_task
def send_reminder_email(todo_name, user_email, reminder_time_str):
    """
    Task to send a reminder email.
    :param todo_name: Name of the task (todo item).
    :param user_email: Email address of the user to send the reminder to.
    :param reminder_time_str: The reminder time as an ISO format string.
    """
    try:
        # Parse the reminder_time_str back into a datetime object
        reminder_time = datetime.fromisoformat(reminder_time_str)

        # Send the email
        send_mail(
            subject='Task Reminder Notification',
            message=f"""
            Hello,
            
            This is a reminder for your task: "{todo_name}".
            Reminder Time: {reminder_time.strftime('%Y-%m-%d %H:%M')}
            
            Thank you for using our service!
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        # Mark the reminder as sent in the database
        reminder = Reminder.objects.filter(todo__todo_name=todo_name, todo__user__email=user_email).first()
        if reminder:
            reminder.is_sent = True
            reminder.save()

    except Exception as e:
        # Log the error if any issue occurs
        print(f"Error sending reminder email: {str(e)}")
