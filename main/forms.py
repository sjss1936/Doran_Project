from django import forms
from .models import User, Post

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
