from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo_name = models.CharField(max_length=128)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.todo_name
    
class Reminder(models.Model):
    todo = models.OneToOneField(todo, on_delete=models.CASCADE, related_name='reminder')
    reminder_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)  # Tracks if the reminder email is sent

    def __str__(self):
        return f"Reminder for {self.todo.todo_name} at {self.reminder_time}"
