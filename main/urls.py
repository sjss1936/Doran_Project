from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('messages/', views.messages, name='messages'),
    path('notifications/', views.notifications, name='notifications'),
    path('create/', views.create, name='create'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]
