from django.contrib import admin
from .models import Reminder, todo

# Register your models here.
admin.site.register(todo)
admin.site.register(Reminder)