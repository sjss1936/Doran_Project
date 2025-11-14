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
from django.db.models import Exists, OuterRef, Q
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

# Local application imports
# 'main' 브랜치의 폼들과 'sonne' 브랜치의 폼을 병합한 버전을 임포트합니다.
from .forms import CustomUserCreationForm, PostForm, ProfileEditForm
from .models import Post, Comment, Like, Notification

# 'main' 브랜치의 모범 사례를 따라 get_user_model() 사용
User = get_user_model()

# 'sonne' 브랜치의 'GET' 방식 뷰를 채택 (병합된 signup.html과 호환됨)
def check_username(request):
    """Check if a username is already taken (for AJAX request)."""
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

# 'main' 브랜치의 DB 연동 뷰를 채택
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

# 'main' 브랜치의 뷰를 채택 (messages 프레임워크 사용)
def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # 회원가입 후 바로 로그인
            username = form.cleaned_data.get('username')
            messages.success(request, f'계정이 생성되었습니다: {username}')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

# 'sonne' 브랜치에만 있던 이메일 활성화 뷰
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
        # 이 템플릿이 필요합니다.
        return render(request, 'main/activation_invalid.html') 

# 'sonne' 브랜치의 표준 뷰 로직을 채택 (form.errors를 템플릿에서 처리)
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
    
    # 참고: placeholder 추가 로직은 forms.py로 이동했으므로 여기서 제거합니다.
    return render(request, 'main/login.html', {'form': form})

# 공통 뷰
def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('index')

# 'sonne' 브랜치에만 있던 placeholder 뷰들
def search(request):
    query = request.GET.get('q')
    if query:
        # 'username' 또는 'name' 필드에서 쿼리를 포함하는 사용자를 검색합니다.
        users = User.objects.filter(
            Q(username__icontains=query) | Q(name__icontains=query)
        )
    else:
        users = User.objects.none() # 쿼리가 없으면 아무도 반환하지 않습니다.

    context = {
        'query': query,
        'users': users
    }
    return render(request, 'main/search.html', context)

def messages_view(request):
    return render(request, 'main/messages.html')

@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    # 알림을 읽음으로 표시
    notifications.update(is_read=True)
    return render(request, 'main/notifications.html', {'notifications': notifications})

# 'main' 브랜치의 뷰 (create 뷰는 공통이었음)
@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            # 'my_profile' 대신 'profile' URL 이름으로 수정 (urls.py 기준)
            return redirect('profile') 
    else:
        form = PostForm()
    return render(request, 'main/create.html', {'form': form})

# 'main' 브랜치의 DB 연동 뷰를 채택
@login_required
def profile(request):
    # 자신의 프로필 페이지로 리디렉션
    return redirect('user_profile', username=request.user.username)

@login_required
def user_profile(request, username):
    # 다른 사용자의 프로필을 보거나, 자신의 프로필을 봄
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().order_by('-created_at')
    if request.user.is_authenticated:
        user_likes = Like.objects.filter(
            post=OuterRef('pk'),
            user=request.user
        )
        posts = posts.annotate(user_has_liked=Exists(user_likes))
    context = {'user': user, 'posts': posts}
    return render(request, 'main/profile.html', context)

# 'main' 브랜치에만 있던 프로필 수정 뷰
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'main/edit_profile.html', {'form': form})

# 'main' 브랜치에만 있던 댓글 추가 뷰
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text: # 빈 댓글 방지
            comment = Comment.objects.create(user=request.user, post=post, text=text)
            # 알림 생성 (자신이 작성한 게시물에 댓글을 달 때는 제외)
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    created_by=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
    # 'profile' 대신 'index'로 리디렉션하는 것이 UX에 더 좋습니다.
    return redirect('index') 

# 'main' 브랜치에만 있던 좋아요 뷰
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        # 알림 생성 (자신이 작성한 게시물에 좋아요를 누를 때는 제외)
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                created_by=request.user,
                notification_type='like',
                post=post
            )
            
    return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})