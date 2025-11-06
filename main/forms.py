from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post

# --- 'develope' (Current change) 브랜치의 코드 ---
class CustomUserCreationForm(UserCreationForm):
    Email = forms.EmailField(
        label="이메일 주소",
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': '이메일 주소'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email') # password 필드는 UserCreationForm에 이미 포함되어 있습니다.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # UserCreationForm의 기본 필드에 placeholder 추가
        self.fields['username'].widget.attrs.update({'placeholder': '사용자 이름'})
        self.fields['password1'].widget.attrs.update({'placeholder': '비밀번호'})
        self.fields['password2'].widget.attrs.update({'placeholder': '비밀번호 확인'})
        
        # Django가 자동으로 생성하는 라벨과 도움말 텍스트 제거
        self.fields['username'].label = ""
        self.fields['email'].label = ""
        self.fields['password1'].label = ""
        self.fields['password2'].label = ""
        self.fields['password1'].help_text = None

# --- 'makePost' (Incoming change) 브랜치의 코드 ---
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # 사용자가 입력받을 필드만 지정
        # fields = ['image', 'caption']