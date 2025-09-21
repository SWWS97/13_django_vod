from django.db import models

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
    created_at = models.DateTimeField("작성일자", auto_now_add=True)
    updated_at = models.DateTimeField("수정일자", auto_now=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"
        # get_category_display : 모델에 choices 사용시에만 가능

    class Meta:
        verbose_name = "블로그"
        verbose_name_plural = "블로그 목록"


