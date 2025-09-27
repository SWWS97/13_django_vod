from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from utils.models import TimeStampModel

User = get_user_model() # get_user_model() : 장고에 설정된 User를 가져오는 함수

# 제목
# 본문
# 작성일자
# 수정일자
# 카테고리
# 작성자 => 추후에 업데이트

class Blog(TimeStampModel):
    CATEGORY_CHOICES = (
        ("free", "자유"),
        ("travel", "여행"),
        ("cat", "고양이"),
        ("dog", "강아지"),
        ("monkey", "원숭이"),
        ("dolphin", "돌고래"),
    )

    category = models.CharField("카테고리", max_length=20,
                                choices=CATEGORY_CHOICES, default="free")
    # choices 옵션 : 장고에서 셀렉트 박스 생성해줌
    title = models.CharField("제목", max_length=100)
    content = models.TextField("본문")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # models.CASCADE => 삭제시 같이 삭제
    # models.PROTECT => 삭제가 불가능(유저를 삭제할려고 할떄 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => NULL(빈값)을 넣는다 => 유저 삭제시 블로그의 author가 null값이 됨


    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"
        # get_category_display : 모델에 choices 사용시에만 가능

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "블로그"
        verbose_name_plural = "블로그 목록"

# category update ORM
# Blog.objects.filter(category="").update(category="free")

#

class Comment(TimeStampModel):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    content = models.CharField("본문", max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.blog.title} 댓글"

    class Meta:
        verbose_name = "댓글"
        verbose_name_plural = "댓글 목록"