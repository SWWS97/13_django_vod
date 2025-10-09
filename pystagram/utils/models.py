from django.db import models


class TimeStampModel(models.Model):
    created_at = models.DateTimeField("작성일자", auto_now_add=True)
    updated_at = models.DateTimeField("수정일자", auto_now=True)

    class Meta:
        abstract = True # Django에게 이 모델은 추상 클래스다 → 테이블로 만들지 마라