from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from todoapp.models import todo
from django.utils.timezone import now
from django.core.mail import send_mail
from django.utils import timezone
from todoapp.models import todo, Reminder
import datetime


def home(request):
    if request.method == 'POST':
        task = request.POST.get('task')
        reminder_time = request.POST.get('reminder_time')
        new_todo = todo(user=request.user, todo_name=task)
        new_todo.save()
        
        # Save the reminder if provided
        if reminder_time:
            reminder_time_parsed = datetime.datetime.strptime(reminder_time, '%Y-%m-%dT%H:%M')
            Reminder.objects.create(todo=new_todo, reminder_time=reminder_time_parsed)
    
    all_todos = todo.objects.filter(user=request.user)
    context = {
        'todos' : all_todos
    }
    return render(request, 'todoapp/todo.html', context)

def loginpage(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = User.objects.filter(email=username_or_email, password=password).first()
        if user:
            username = user.username  # Get the corresponding username
        else:
            username = username_or_email
        
        validate_user = authenticate(request, username=username, password=password)
        if validate_user is not None:
            login(request, validate_user)
            return redirect('home-page')
        else:
            messages.error(request, 'User does not exist or password do not match!')
            return redirect('loginpage')
        
    return render(request, 'todoapp/login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_email = request.POST.get('email')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmpassword')

        if password != confirmpassword:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 Characters.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=user_email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create(
            username=username,
            email=user_email,
            password=make_password(password),
        )
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect('loginpage')

    return render(request, 'todoapp/register.html')


def logout_user(request):
    logout(request)
    return redirect('loginpage') 


def DeleteTask(request, name):
    get_todo = todo.objects.filter(user=request.user, todo_name=name)
    get_todo.delete()
    return redirect('home-page')

def Update (request, name):
    get_todo = todo.objects.get(user=request.user, todo_name=name)
    get_todo.status = True
    get_todo.save()
    return redirect('home-page')

def set_reminder(request, name):
    if request.method == 'POST':
        reminder_time = request.POST.get('reminder_time')
        try:
            todo_item = todo.objects.get(todo_name=name, user=request.user)
            reminder_time_parsed = datetime.datetime.strptime(reminder_time, '%Y-%m-%dT%H:%M')
            reminder = Reminder.objects.create(todo=todo_item, reminder_time=reminder_time_parsed)
            reminder.save()
            messages.success(request, "Reminder set successfully.")
        except todo.DoesNotExist:
            messages.error(request, "Task not found or unauthorized access.")
    return redirect('home-page')
