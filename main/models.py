from django.db import models
from django.contrib.auth.models import User # 장고의 기본 사용자 모델 가져오기

# Create your models here.
class Post(models.Model):
    # author (작성자): User 모델과 연결. 유저가 삭제되면 게시물도 삭제
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    # image (사진): 이미지/동영상 파일 업로드
    image = models.ImageField(upload_to='posts/images/')
    # caption (내용): 글 내용
    caption = models.TextField()
    # created_at (작성일): 글 작성 시 자동으로 현재 시간 저장
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}의 게시물"
