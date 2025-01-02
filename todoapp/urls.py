from django.urls import path 
from .import views

urlpatterns = [
    path('home/', views.home, name='home-page'),
    path('', views.loginpage, name='loginpage'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('delete-task/<str:name>/', views.DeleteTask, name='delete'),
    path('update/<str:name>/', views.Update, name='update'),
    path('set_reminder/<str:name>/', views.set_reminder, name='set_reminder'),
    
]