from django.urls import path
from . import views

urlpatterns = [
    # --- 공통 URL ---
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
    path('messages/<str:username>/send/', views.send_message, name='send_message'),
    path('notifications/', views.notifications, name='notifications'),
    path('create/', views.create, name='create'),
    
    # --- 인증 관련 URL (공통 + 'sonne' 브랜치) ---
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('check_username/', views.check_username, name='check_username'),
    # 'sonne' 브랜치에만 있던 URL
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'), 

    # --- 'main' 브랜치에만 있던 URL (게시물, 프로필) ---
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    
    # --- 프로필 URL (순서 중요!) ---
    # 더 구체적인 'edit' 경로가 먼저 와야 합니다. ('main' 브랜치)
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    # 공통 URL
    path('profile/', views.profile, name='profile'), 
]