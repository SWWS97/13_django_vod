from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model() # get_user_model() : 장고에 설정된 User를 가져오는 함수

# 제목
# 본문
# 작성일자
# 수정일자
# 카테고리
# 작성자 => 추후에 업데이트

class Blog(models.Model):
    CATEGORY_CHOICES = (
        ("free", "자유"),
        ("travel", "여행"),
        ("cat", "고양이"),
        ("dog", "강아지"),
        ("monkey", "원숭이"),
        ("dolphin", "돌고래"),
    )

    category = models.CharField("카테고리", max_length=20,
                                choices=CATEGORY_CHOICES)
    # choices 옵션 : 장고에서 셀렉트 박스 생성해줌
    title = models.CharField("제목", max_length=100)
    content = models.TextField("본문")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # models.CASCADE => 삭제시 같이 삭제
    # models.PROTECT => 삭제가 불가능(유저를 삭제할려고 할떄 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => NULL(빈값)을 넣는다 => 유저 삭제시 블로그의 author가 null값이 됨

    created_at = models.DateTimeField("작성일자", auto_now_add=True)
    updated_at = models.DateTimeField("수정일자", auto_now=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"
        # get_category_display : 모델에 choices 사용시에만 가능

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "블로그"
        verbose_name_plural = "블로그 목록"


