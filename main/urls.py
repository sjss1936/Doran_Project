from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('messages/', views.messages_view, name='messages'),
    path('notifications/', views.notifications, name='notifications'),
    path('create/', views.create, name='create'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('check_username/', views.check_username, name='check_username'),
    path('logout/', views.logout_view, name='logout'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
