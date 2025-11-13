from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('name', 'email', 'phone_number')
        labels = {
            'username': '아이디',
            'name': '이름',
            'email': '이메일',
            'phone_number': '전화번호',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = '비밀번호'
        self.fields['password2'].label = '비밀번호 확인'

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'bio', 'profile_picture', 'cover_image']
        labels = {
            'name': '이름',
            'bio': '자기소개',
            'profile_picture': '프로필 사진',
            'cover_image': '커버 이미지',
        }
