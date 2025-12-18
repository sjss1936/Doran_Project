from django.urls import path
from . import views

urlpatterns = [
    # --- Common URLs ---
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
    path('notifications/', views.notifications, name='notifications'),
    path('create/', views.create, name='create'),
    
    # --- Authentication URLs ---
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('check_username/', views.check_username, name='check_username'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'), 

    # --- Post and Profile URLs ---
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    
    # --- Profile URLs (order is important) ---
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/replies/', views.user_replies, name='user_replies'),
    path('profile/<str:username>/likes/', views.user_likes, name='user_likes'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('profile/', views.profile, name='profile'), 
]