from io import BytesIO
from pathlib import Path

from PIL import Image
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
    thumbnail = models.ImageField("썸네일", null=True, blank=True, upload_to="blog/%Y/%m/%d/thumbnail")
    # ImageField
    # 2025/9/30일 -> media/blog/2025/9/30/이미지파일.jpg
    # 기본적으로 varchar로 되어있고 FileField와 같지만 이미지인지 검증해서 이미지만 업로드 하게 되어있음.
    # 장고 media 경로에 이미지를 저장 시키고 그 경로를 DB에 텍스트로 저장함

    # null : DB에 null값 허용
    # blank : form에서 입력할 때 빈값 허용

    # models.CASCADE => 삭제시 같이 삭제
    # models.PROTECT => 삭제가 불가능(유저를 삭제할려고 할떄 블로그가 있으면 유저 삭제가 불가능)
    # models.SET_NULL => NULL(빈값)을 넣는다 => 유저 삭제시 블로그의 author가 null값이 됨


    def __str__(self):
        return f"[{self.get_category_display()}] {self.title[:10]}"
        # get_category_display : 모델에 choices 사용시에만 가능

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"blog_pk": self.pk})

    def get_thumbnail_image_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image:
            return self.image.url
        return None

    def save(self, *args, **kwargs):
        if not self.image:
            return super().save(*args, **kwargs)

        image = Image.open(self.image)
        image.thumbnail((300, 300))
        image_path = Path(self.image.name)

        thumbnail_name = image_path.stem # stem : /blog/2025/09/30/이미지.png => 확장자(.png)가 빠진 이미지를 가져옴. => 이미지
        thumbnail_extension = image_path.suffix.lower() # suffix : /blog/2025/09/30/이미지.png => 확장자(.png)만 들고옴 => .png
        thumbnail_filename = f"{thumbnail_name}_thumb{thumbnail_extension}" # 최종적으로 이미지_thumb.png 이렇게 만들어짐

        if thumbnail_extension in [".jpg", ".jpeg"]:
            file_type = "JPEG"
        elif thumbnail_extension == ".gif":
            file_type = "GIF"
        elif thumbnail_extension == ".png":
            file_type = "PNG"
        else:
            return super().save(*args, **kwargs)

        temp_thumb = BytesIO()
        image.save(temp_thumb, file_type)
        temp_thumb.seek(0)

        self.thumbnail.save(thumbnail_filename, temp_thumb, save=False)
        temp_thumb.close()
        return super().save(*args, **kwargs)


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