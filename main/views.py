# Doran_Project/main/views.py (이 코드로 덮어쓰세요)

# --- 1. 모든 Import 문 합치기 (중복 제거) ---
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Local application imports
from .forms import CustomUserCreationForm, PostForm
from .models import Post

# --- 2. index 뷰 (makePost 브랜치의 '진짜 DB' 버전 사용) ---
def index(request):
    """Main feed page."""
    # 'makePost'의 DB 연동 코드를 사용
    posts = Post.objects.all().order_by('-created_at')
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

# --- 3. develope 브랜치의 회원가입/로그인 기능 ---
def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True # 사용자를 바로 활성화 (develope 브랜치 로직)
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
        # activation_invalid.html 템플릿이 필요합니다.
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
    
    # placeholder 추가 로직 (develope 브랜치 로직)
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

# --- 4. 기타 플레이스홀더 뷰 ---
def search(request):
    return render(request, 'main/search.html')

def messages(request):
    return render(request, 'main/messages.html')

def notifications(request):
    return render(request, 'main/notifications.html')

# --- 5. makePost 브랜치의 '게시물 생성' 기능 ---
@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    
    context = {'form': form}
    return render(request, 'main/create.html', context)

# --- 6. develope 브랜치의 '프로필' 뷰 (아직 가짜 데이터 사용) ---
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
    # (참고: profile 페이지의 posts도 나중에는 DB에서 가져와야 함)
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

# --- 7. 충돌로 인해 중복된 하단 함수들 제거 ---
# (파일 끝에 있던 login_view, signup_view, profile 등은 
#  위쪽의 정교한 함수들과 중복되므로 삭제했습니다.)