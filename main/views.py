from django.shortcuts import render

def index(request):
    posts = [
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png', # Assuming user will add profile1.jpg
            'image_url': '/static/main/img/aa.jpg', # Assuming user will add post1.jpg
            'likes': 1234,
            'caption': '나 좀 잘생긴 거 같아.'
        },
        {
            'username': 'sikboyyy',
            'profile_picture': '/static/main/img/user1.png', # Assuming user will add profile2.jpg
            'image_url': '/static/main/img/bb.jpg', # Assuming user will add post2.jpg
            'likes': 567,
            'caption': '이건 좀 귀여운듯.'
        }
    ]
    context = {'posts': posts}
    return render(request, 'main/index.html', context)

def search(request):
    return render(request, 'main/search.html')

def messages(request):
    return render(request, 'main/messages.html')

def notifications(request):
    return render(request, 'main/notifications.html')

def create(request):
    return render(request, 'main/create.html')

def profile(request):
    return render(request, 'main/profile.html')

def login_view(request):
    return render(request, 'main/login.html')

def signup_view(request):
    return render(request, 'main/signup.html')
