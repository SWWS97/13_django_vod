import re

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images") # related_name 기본값 : "postimage_set"
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


# 태그 : 태그와 포스트는 N:M 관계
class Tag(TimeStampModel):
    tag = models.CharField("태그", max_length=100)
    post = models.ManyToManyField(Post, related_name="tags") # 중간 테이블 name은 "tags"로 설정

    def __str__(self):
        return self.tag

# 댓글
class Comment(TimeStampModel):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    content = models.CharField("내용", max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post} | {self.user}"

# @receiver : 특정 이벤트(시그널)이 발생했을 때, 어떤 함수를 자동으로 실행해라
# post_save : 세이브(저장)하고 난후 @receiver 함수 호출 여기선 Post모델이 저장되고 난 이후에
# pre_save : 세이브(저장)하기 전에 @receiver 함수 호출
# r"#(\w{1,100})(?=\s|$)" → # 뒤에 오는 1~100자 단어를 찾고, 공백이나 문장 끝에서 멈춤
@receiver(post_save, sender=Post)
def post_post_save(sender, instance, created, **kwargs):
    hashtags = re.findall(r"#(\w{1,100})(?=\s|$)", instance.content) # 여기서 instance.content는 Post 모델에 content

    # clear() → 예전 태그 스티커 싹 떼기 : 해시태그는 수정,삭제 될수도 있기 때문에
    instance.tags.clear() # 연결 되어있는 tags 중계 모델을 삭제 (중간 테이블에서 연결만 지우는 것, Tag 자체는 삭제 안 함)

    # get_or_create : 해당 태그가 DB에 있으면 가져오고, 없으면 새로 만든다
    # 반환값은 (Tag객체, created여부(True, False)) 튜플
    if hashtags:
        tags = [
            Tag.objects.get_or_create(tag=hashtag)
            for hashtag in hashtags
        ]
        # 반환값은 (Tag객체, created여부(True, False)) 튜플이므로 안쓰는 값(bool)는 _ 이렇게 표현해서 Tag만 추출
        tags = [tag for tag, _ in tags]

        # add() → 새로 분석한 태그 스티커 다시 붙이기
        instance.tags.add(*tags) # 위에서 새로 추출한 태그들을 Post에 새로 연결
