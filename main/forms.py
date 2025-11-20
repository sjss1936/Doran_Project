from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    """
    'main' 브랜치의 커스텀 필드('name', 'email', 'phone_number')를 사용하면서,
    'sonne' 브랜치의 스타일(placeholder 사용, label 제거)을 적용합니다.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'username': '아이디',
            'name': '이름',
            'email': '이메일',
            'phone_number': '전화번호',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
        }

        for field_name, placeholder_text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'placeholder': placeholder_text})
                self.fields[field_name].label = ""

        if 'password1' in self.fields:
            self.fields['password1'].help_text = None

class PostForm(forms.ModelForm):
    """
    'main' 브랜치의 PostForm에 'sonne' 브랜치의 스타일을 적용합니다.
    """
    class Meta:
        model = Post
        fields = ['image', 'caption']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = ""
        self.fields['caption'].label = ""
        self.fields['caption'].widget.attrs.update({'placeholder': '내용을 입력하세요...'})


class ProfileEditForm(forms.ModelForm):
    """
    'main' 브랜치의 ProfileEditForm에 'sonne' 브랜치의 스타일을 적용합니다.
    """
    class Meta:
        model = User
        fields = ['name', 'bio', 'profile_picture', 'cover_image']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        placeholders = {
            'name': '이름',
            'bio': '자기소개',
        }

        for field_name, placeholder_text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'placeholder': placeholder_text})
                self.fields[field_name].label = ""

        if 'profile_picture' in self.fields:
            self.fields['profile_picture'].label = "프로필 사진"
        if 'cover_image' in self.fields:
            self.fields['cover_image'].label = "커버 이미지"
