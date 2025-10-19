from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from utils.models import TimeStampModel


# 커스텀 매니저, 유저 작성
# 추후에 다른 서비스에서 사용할 때 이걸 토대로 작성해도 됨

# 장고 유저 매니저 오버라이딩
# UserManager = User.objects.all() 여기서 objects : 매니저 부분
class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("올바른 이메일을 입력하세요.")

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password) # password 해시화
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password): # python manage.py createsuperuser 명령어
        user = self.create_user(email, password)
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

# user.save() => 기본 DB('default')에 저장
# user.save(using=self._db) => 현재 매니저가 연결된 DB에 맞춰 저장 (다중 DB 대응용)
# using=self._db는 “이 매니저가 현재 연결 중인 DB에 맞춰 저장해라”는 의미로,
# 다중 데이터베이스 환경에서도 코드가 깨지지 않도록 해주는 안전장치

# 암호화는 복호화가 가능 : qwer1234 -> 암호화 -> sadasfasf231 -> 복호화 -> qwer1234
# 해시화는 복호화가 불가능 : qwer1234 -> sadas / fasf231 -> 암호화(sadas) -> 암호화를 반복 -> fsafgjwg -> 복호화가 불가능
# SHA-256


# 장고 유저 모델 오버라이딩
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email",
        unique=True,
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    nickname = models.CharField("nickname", max_length=20, unique=True)
    # 나를 팔로우 하는 사람이 팔로워
    # 내가 팔로우 하는 사람이 팔로잉
    # User N:N User이기 때문에 ManyToMany
    # User테이블(본인) 참조 할 때는 "self" 사용
    # a <=> b symmetrical=Ture
    # a => b symmetrical=False
    # through : 기본 중계 테이블 말고 아래에서 만든 중계 테이블 사용
    # following : 팔로우 하는 사람 => through_fields 순서는 from_user : 자신, to_user : 팔로우 대상
    following = models.ManyToManyField(
        "self", symmetrical=False, related_name="followers",
        through="UserFollowing", through_fields=("from_user", "to_user")
    )

    objects = UserManager()
    # Django 기본 User의 로그인 ID는 username 필드인데, 이걸 email 필드로 바꾸겠다는 뜻
    # => 로그인할 때 “username” 대신 “email”을 입력
    USERNAME_FIELD = "email"
    # Django 내부적으로 이메일 관련 기능(비밀번호 재설정 메일 등)에서 어떤 필드를 이메일로 쓸지 지정하는 설정
    # => 이 User의 이메일 주소는 email 필드에 있다”고 알려줌
    EMAIL_FIELD = "email"
    # createsuperuser 명령으로 관리자 계정을 만들 때 추가로 필수 입력받을 필드를 적는 리스트
    # => 여기에 아무것도 안 넣으면, 이메일(USERNAME_FIELD)과 비밀번호만 입력받음
    REQUIRED_FIELDS = []

    # Admin 페이지 등에서 모델 이름이 한글로 예쁘게 보이게 하는 설정
    class Meta:
        verbose_name = "유저"
        verbose_name_plural = f"{verbose_name}목록 "
    # 유저의 전체 이름을 반환하는 함수
    def get_full_name(self):
            return self.nickname
    # 유저의 짧은 이름(표시용 이름) 을 반환하는 함수
    def get_short_name(self):
            return self.nickname
    # User object (1)” 같은 기본 문구 대신 그 유저의 닉네임이 나오게 하는 함수
    def __str__(self):
        return self.nickname
    # 유저가 “모든 권한이 있다”고 처리
    def has_perm(self, perm, obj=None):
        return True
    # 유저가 "모든 앱 접근 가능"
    def has_module_perms(self, app_label):
        return True
    # Django 관리자(admin 페이지)에 접근할 수 있는지를 결정하는 속성
    # is_staff가 True이면 admin 페이지 로그인 가능
    # is_admin 값이 True이면 staff로 취급하도록 연결
    @property
    def is_staff(self):
        return self.is_admin
    # 슈퍼유저(모든 권한을 가진 최고 관리자) 여부를 반환
    # is_admin이 True면 슈퍼유저로 간주
    @property
    def is_superuser(self):
        return self.is_admin
# @property
# @property는 파이썬에서 “메서드를 마치 변수(속성)처럼 쓸 수 있게 만들어주는 기능”
# 즉, 함수 호출 괄호 () 없이도 값을 가져올 수 있게 해주는 데코레이터
# 원래는 user.is_superuser()
# @property 사용 =>  user.is_superuser
# 이유 : 괄호 없이 깔끔하게 접근하기 위해

class UserFollowing(TimeStampModel):
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_followers")
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_following")

    class Meta:
        unique_together = ("to_user", "from_user")
    # to_user 1, from_user 2 O
    # to_user 1, from_user 3 O
    # to_user 1, from_user 4 O

    # to_user 1, from_user 2 X => 기존에 있던걸 다시 만들려고 시도하면 오류
