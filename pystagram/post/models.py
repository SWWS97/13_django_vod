from django.contrib.auth import get_user_model
from django.db import models

from utils.models import TimeStampModel

User = get_user_model()

class Post(TimeStampModel):
    content = models.TextField("본문")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"[{self.user}] post" # User 모델에 def __str__ 에서 정의된 nickname 가져옴

    class Meta:
        verbose_name = "포스트"
        verbose_name_plural = f"{verbose_name} 목록"


class PostImage(TimeStampModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField("이미지", upload_to="post/%Y/%m/%d")

    def __str__(self):
        return f"{self.post} image" # User의 def __str__ 에서 정의된 nickname

    class Meta:
        verbose_name = "이미지"
        verbose_name_plural = f"{verbose_name} 목록"


# Post
    # 이미지(여러개)
    # 글
    # 작성자
    # 작성일자
    # 수정일자


# 태그
# 댓글
