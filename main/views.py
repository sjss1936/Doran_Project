from django.http import JsonResponse
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, PostForm, ProfileEditForm
from .models import Post, Comment, Like
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

def check_username(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        username = data.get('username')
        if User.objects.filter(username=username).exists():
            return JsonResponse({'message': '이미 사용중인 아이디입니다.'})
        else:
            return JsonResponse({'message': '사용 가능한 아이디입니다.'})
    return JsonResponse({'message': '잘못된 요청입니다.'}, status=400)

def index(request):
    posts = Post.objects.all().order_by('-created_at')
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

def search(request):
    return render(request, 'main/search.html')

def messages_view(request):
    return render(request, 'main/messages.html')

def notifications(request):
    return render(request, 'main/notifications.html')

@login_required
def create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('my_profile')
    else:
        form = PostForm()
    return render(request, 'main/create.html', {'form': form})

@login_required
def profile(request):
    posts = request.user.posts.all()
    context = {'user': request.user, 'posts': posts}
    return render(request, 'main/profile.html', context)

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

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'계정이 생성되었습니다: {username}')
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        Comment.objects.create(user=request.user, post=post, text=text)
    return redirect('profile')

@login_required
def like_post(request, post_id):
    post = Post.objects.get(id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'likes_count': post.likes.count(), 'liked': liked})