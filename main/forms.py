from django import forms
from django.contrib.auth.forms import UserCreationForm
# 'main' 브랜치의 커스텀 User 모델과 Post 모델을 임포트합니다.
from .models import User, Post

class CustomUserCreationForm(UserCreationForm):
    """
    'main' 브랜치의 커스텀 필드('name', 'email', 'phone_number')를 사용하면서,
    'sonne' 브랜치의 스타일(placeholder 사용, label 제거)을 적용합니다.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        # 'main' 브랜치의 필드 정의를 사용합니다.
        fields = UserCreationForm.Meta.fields + ('name', 'email', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 'main' 브랜치의 label 텍스트를 placeholder 텍스트로 활용합니다.
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
                # 'sonne' 브랜치 스타일: placeholder 추가
                self.fields[field_name].widget.attrs.update({'placeholder': placeholder_text})
                # 'sonne' 브랜치 스타일: label 제거
                self.fields[field_name].label = ""

        # 'sonne' 브랜치 스타일: password1 필드의 도움말 텍스트 제거
        if 'password1' in self.fields:
            self.fields['password1'].help_text = None

# --- 'main' 브랜치에만 있던 폼들 ---

class PostForm(forms.ModelForm):
    """
    'main' 브랜치의 PostForm에 'sonne' 브랜치의 스타일을 적용합니다.
    """
    class Meta:
        model = Post
        fields = ['image', 'caption']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 'sonne' 스타일 적용
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
        
        # 'main' 브랜치의 label 텍스트를 placeholder 텍스트로 활용
        placeholders = {
            'name': '이름',
            'bio': '자기소개',
        }

        for field_name, placeholder_text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({'placeholder': placeholder_text})
                self.fields[field_name].label = ""

        # 이미지/파일 필드는 placeholder가 의미 없으므로 label만 제거
        if 'profile_picture' in self.fields:
            self.fields['profile_picture'].label = "프로필 사진" # 파일 필드는 placeholder 대신 label을 남겨두는 것이 좋습니다.
        if 'cover_image' in self.fields:
            self.fields['cover_image'].label = "커버 이미지"