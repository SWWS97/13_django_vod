from django.db import models

# Model = DB의 테이블
# Field = DB의 컬럼

# 북마크
# 이름 => char
# URL 주소 => char


class Bookmark(models.Model):
    name = models.CharField("이름", max_length=100)
    url = models.URLField("URL") # URLField = url validation
    created_at = models.DateTimeField("생성일시", auto_now_add=True)
    updated_at = models.DateTimeField("수정일시", auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "북마크"
        verbose_name_plural = "북마크 목록"

# makemigrations => migration.py 파일을 만듦.
# 실제 DB에는 영향이 X => 실제 DB에 넣기 위한 정의된 파일을 만듦.

# migrate => migrations/ 폴더 안에 있는 migration 파일들을 실제 DB에 적용하는 명령어

# makemigration => 깃의 commit => github에 적용 X => DB에 적용 X, 적용할 파일을 생성
# migrate => 깃의 push => github에 적용 O, 로컬에 있는 커밋 기록 사용 => DB에 적용 O, migrations 파일을 가지고 적용
