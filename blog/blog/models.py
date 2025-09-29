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

    # choices 옵션 : 장고에서 셀렉트 박스 생성해줌
    category = models.CharField("카테고리", max_length=20,
                                choices=CATEGORY_CHOICES, default="free")

    title = models.CharField("제목", max_length=100)
    content = models.TextField("본문")
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    image = models.ImageField("이미지", null=True, blank=True, upload_to="blog/%Y/%m/%d") # "blog/%Y-%m-%d"
    # ImageField
    # 2025/9/30일 -> media/blog/2025/9/30/이미지파일.jpg
    # 기본적으로 varchar로 되어있고 FileField와 같지만 이미지인지 검증해서 이미지만 업로드 하게 되어있음.
    # 장고 media 경로에 이미지를 저장 시키고 그 경로를 DB에 텍스트로 저장함

    # models.CASCADE => 삭제시 같이 삭제
    # models.PROTECT => 삭제가 불가능(유저를 삭제할려고 할떄 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => NULL(빈값)을 넣는다 => 유저 삭제시 블로그의 author가 null값이 됨


    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"
        # get_category_display : 모델에 choices 사용시에만 가능

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"blog_pk": self.pk})

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
        ordering = ("-created_at", "-id")