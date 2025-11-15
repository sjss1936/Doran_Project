# Django-related imports
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Local application imports
from .forms import CustomUserCreationForm

# Create your views here.

def index(request):
    """Main feed page."""
    # This is sample data. You might want to fetch real data from the database.
    posts = [
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png',
            'image_url': '/static/main/img/aa.jpg',
            'likes': 1234,
            'caption': '나 좀 잘생긴 거 같아.'
        },
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png',
            'image_url': '/static/main/img/bb.jpg',
            'likes': 567,
            'caption': '이건 좀 귀여운듯.'
        }
    ]
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True # 사용자를 바로 활성화
            user.save()
            login(request, user) # 회원가입 후 바로 로그인
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
    
    form.fields['username'].widget.attrs.update({'placeholder': '사용자 이름'})
    form.fields['password'].widget.attrs.update({'placeholder': '비밀번호'})
    
    return render(request, 'main/login.html', {'form': form})

def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('index')

def check_username(request):
    """Check if a username is already taken (for AJAX request)."""
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def search(request):
    return render(request, 'main/search.html')

def notifications(request):
    return render(request, 'main/notifications.html')

def create(request):
    return render(request, 'main/create.html')

def profile(request):
    user_profile = {
        'name': 'sikboyyy',
        'username': '@sikboyyy',
        'bio': 'This is my Doran project. I love coding and building awesome things.',
        'banner_url': '/static/main/img/bb.jpg',
        'profile_picture_url': '/static/main/img/user1.png',
        'following': 123,
        'followers': 456,
    }
    posts = [
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png',
            'image_url': '/static/main/img/aa.jpg',
            'likes': 1234,
            'caption': '나 좀 잘생긴 거 같아.'
        },
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png',
            'image_url': '/static/main/img/bb.jpg',
            'likes': 567,
            'caption': '이건 좀 귀여운듯.'
        }
    ]
    context = {
        'user': user_profile,
        'posts': posts
    }
    return render(request, 'main/profile.html', context)

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Message, Profile # Profile is still needed for user info

# These views are placeholders and can be developed further.
@login_required
def messages(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'main/messages.html', {'users': users})

@login_required
def room_ajax(request, room_name):
    room, created = Room.objects.get_or_create(name=room_name)
    messages = Message.objects.filter(room=room).order_by('timestamp').select_related('user__profile')

    # Extract other username from room_name
    usernames_in_room = room_name.split('_')[1:] # ['user1', 'user2']
    other_username = next((u for u in usernames_in_room if u != request.user.username), None)
    
    other_user_profile_picture_url = None
    if other_username:
        try:
            other_user = User.objects.get(username=other_username)
            if other_user.profile.profile_picture:
                other_user_profile_picture_url = other_user.profile.profile_picture.url
        except User.DoesNotExist:
            pass # Handle case where other user might not exist

    return render(request, 'main/messages.html', {
        'room_name': room_name,
        'messages': messages,
        'username': request.user.username,
        'other_user_profile_picture_url': other_user_profile_picture_url,
    })

@csrf_exempt
@login_required
def send_message_ajax(request):
    if request.method == 'POST':
        message_content = request.POST.get('message')
        room_name = request.POST.get('room_name')
        username = request.user.username

        print(f"send_message_ajax: Received message_content='{message_content}', room_name='{room_name}', username='{username}'")

        try:
            user = User.objects.get(username=username)
            room = Room.objects.get(name=room_name)
            message = Message.objects.create(user=user, room=room, content=message_content)
            
            profile_picture_url = ''
            if hasattr(user, 'profile') and user.profile.profile_picture:
                profile_picture_url = user.profile.profile_picture.url

            print(f"send_message_ajax: Message saved. User: {user.username}, Room: {room.name}")
            return JsonResponse({
                'status': 'success',
                'message': message.content,
                'username': user.username,
                'profile_picture_url': profile_picture_url,
                'timestamp': message.timestamp.isoformat(),
            })
        except (User.DoesNotExist, Room.DoesNotExist) as e:
            print(f"send_message_ajax: User or Room Does Not Exist error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            print(f"send_message_ajax: Unexpected error: {e}")
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {e}'}, status=500)
    print("send_message_ajax: Invalid request method (not POST)")
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def get_messages_ajax(request, room_name):
    room, created = Room.objects.get_or_create(name=room_name)
    last_message_id = request.GET.get('last_message_id', 0)
    
    messages = Message.objects.filter(room=room, id__gt=last_message_id).order_by('timestamp').select_related('user__profile')
    
    messages_data = []
    for message in messages:
        profile_picture_url = message.user.profile.profile_picture.url if message.user.profile.profile_picture else ''
        messages_data.append({
            'id': message.id,
            'message': message.content,
            'username': message.user.username,
            'profile_picture_url': profile_picture_url,
            'timestamp': message.timestamp.isoformat(),
        })
    
    return JsonResponse({'messages': messages_data})
