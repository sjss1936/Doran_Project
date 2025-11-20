# Django-related imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.db.models import Exists, OuterRef, Q, Max
import json
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Local application imports
from .forms import CustomUserCreationForm, PostForm, ProfileEditForm
from .models import Post, Comment, Like, Notification, Follow, Message

# Get the User model
User = get_user_model()

def check_username(request):
    """Check if a username is already taken (for AJAX request)."""
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def index(request):
    posts = Post.objects.all().order_by('-created_at')
    if request.user.is_authenticated:
        user_likes = Like.objects.filter(
            post=OuterRef('pk'),
            user=request.user
        )
        posts = posts.annotate(user_has_liked=Exists(user_likes))
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in after signup
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def activate(request, uidb64, token):
    """Activate user account from email link."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'main/activation_invalid.html')

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('index')

def search(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query)
        )
    else:
        users = User.objects.none()
    context = {
        'query': query,
        'users': users
    }
    return render(request, 'main/search.html', context)

@login_required
def messages_view(request):
    sent_to_users = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from_users = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    
    all_participant_ids = list(set(list(sent_to_users) + list(received_from_users)))
    
    if request.user.id in all_participant_ids:
        all_participant_ids.remove(request.user.id)

    conversations = []
    for user_id in all_participant_ids:
        other_user = User.objects.get(id=user_id)
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
        ).order_by('-timestamp').first()
        
        unread_count = Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).count()
        
        conversations.append({
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else None, reverse=True)

    context = {
        'conversations': conversations
    }
    return render(request, 'main/messages.html', context)

@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    notifications.update(is_read=True)
    return render(request, 'main/notifications.html', {'notifications': notifications})

@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('profile')
    else:
        form = PostForm()
    return render(request, 'main/create.html', {'form': form})

@login_required
def profile(request):
    return redirect('user_profile', username=request.user.username)

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().order_by('-created_at')

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        
        user_likes = Like.objects.filter(
            post=OuterRef('pk'),
            user=request.user
        )
        posts = posts.annotate(user_has_liked=Exists(user_likes))

    follower_count = user.followers.count()
    following_count = user.following.count()

    context = {
        'user': user,
        'posts': posts,
        'is_following': is_following,
        'follower_count': follower_count,
        'following_count': following_count,
    }
    return render(request, 'main/profile.html', context)

@login_required
def follow_toggle(request, username):
    if request.method == 'POST':
        to_user = get_object_or_404(User, username=username)
        from_user = request.user

        if from_user == to_user:
            return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself.'}, status=400)

        follow, created = Follow.objects.get_or_create(from_user=from_user, to_user=to_user)

        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True

        follower_count = to_user.followers.count()
        following_count = from_user.following.count()

        return JsonResponse({
            'status': 'ok',
            'is_following': is_following,
            'follower_count': follower_count,
            'following_count': following_count
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def send_message(request, username):
    if request.method == 'POST':
        receiver = get_object_or_404(User, username=username)
        sender = request.user
        data = json.loads(request.body)
        content = data.get('content')

        if content:
            Message.objects.create(sender=sender, receiver=receiver, content=content)
            return JsonResponse({'status': 'ok', 'message': 'Message sent.'})
        return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    context = {
        'other_user': other_user,
        'messages': messages
    }
    return render(request, 'main/messages.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'main/edit_profile.html', {'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            comment = Comment.objects.create(user=request.user, post=post, text=text)
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    created_by=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
    return redirect('index')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                created_by=request.user,
                notification_type='like',
                post=post
            )
            
    return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})
