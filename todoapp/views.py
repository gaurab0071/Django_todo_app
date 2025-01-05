from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from todoapp.models import todo, Reminder
from django.utils.timezone import now
from django.utils import timezone
from .tasks import send_reminder_email
from django.core.mail import send_mail
from django.conf import settings
import datetime


def home(request):
    if request.method == 'POST':
        task = request.POST.get('task')
        if not task:
            messages.error(request, "Task cannot be empty.")
            return redirect('home-page')

        new_todo = todo(user=request.user, todo_name=task)
        new_todo.save()

        messages.success(request, "Task added successfully.")
        return redirect('home-page')

    # Fetch all tasks for the logged-in user
    all_todos = todo.objects.filter(user=request.user).exclude(todo_name="")
    context = {
        'todos': all_todos
    }
    return render(request, 'todoapp/todo.html', context)


def loginpage(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')

        # Handle email or username-based authentication
        user = User.objects.filter(email=username_or_email).first()
        username = user.username if user else username_or_email

        validate_user = authenticate(request, username=username, password=password)
        if validate_user is not None:
            login(request, validate_user)
            return redirect('home-page')
        else:
            messages.error(request, 'Invalid username/email or password.')
            return redirect('loginpage')

    return render(request, 'todoapp/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        # Validation checks
        if password != confirmpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Save user
        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
        )
        user.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('loginpage')

    return render(request, 'todoapp/register.html')


def logout_user(request):
    logout(request)
    return redirect('loginpage')


def DeleteTask(request, name):
    try:
        todo_item = todo.objects.get(user=request.user, todo_name=name)
        todo_item.delete()
        messages.success(request, "Task deleted successfully.")
    except todo.DoesNotExist:
        messages.error(request, "Task not found.")
    return redirect('home-page')


def Update(request, name):
    try:
        todo_item = todo.objects.get(user=request.user, todo_name=name)
        todo_item.status = True
        todo_item.save()
        messages.success(request, "Task marked as completed.")
    except todo.DoesNotExist:
        messages.error(request, "Task not found.")
    return redirect('home-page')


def set_reminder(request, name):
    if request.method == 'POST':
        reminder_time = request.POST.get('reminder_time')
        try:
            todo_item = todo.objects.get(user=request.user, todo_name=name)

            # Check if a reminder is already set for the task
            if Reminder.objects.filter(todo=todo_item).exists():
                messages.error(request, "A reminder is already set for this task.")
                return redirect('home-page')

            # Parse the reminder time
            reminder_time_parsed = datetime.datetime.strptime(reminder_time, '%Y-%m-%dT%H:%M')

            # Create the Reminder object
            reminder = Reminder.objects.create(
                todo=todo_item,
                reminder_time=reminder_time_parsed,
                is_sent=False
            )

            # Schedule the email task
            send_reminder_email.apply_async(
                (todo_item.todo_name, request.user.email, reminder_time_parsed.isoformat()),
                eta=reminder_time_parsed
            )

            messages.success(request, "Reminder set successfully. An email will be sent at the scheduled time.")
        except todo.DoesNotExist:
            messages.error(request, "Task not found or unauthorized access.")
        except ValueError:
            messages.error(request, "Invalid reminder date and time format. Please use the correct format.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred while setting the reminder: {str(e)}")
    return redirect('home-page')
