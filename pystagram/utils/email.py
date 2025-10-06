from typing import Union, List

from django.conf import settings
from django.core.mail import send_mail


# to_email: Union[str, List[str]]: Python은 동적 타입 언어라서, 원래는 타입 제한이 없음
# 하지만 Union을 쓰면 코드 편집기나 타입체커(MyPy)가
# “이 함수는 to_email로 문자열 또는 문자열 리스트만 받을 수 있어” 라고 인식하게 됨
# isinstance()는 객체가 특정 타입(클래스)의 인스턴스인지 확인하는 내장 함수
def send_email(subject, message, to_email):
    to_email = to_email if isinstance(to_email, list) else [to_email, ]
    # if isinstance(to_email, list):
    #     to_email = to_email
    # else:
    #     to_email = [to_email, ]

    # send_mail()은 Django 내장 이메일 발송 함수이며,
    # settings.py의 SMTP 설정만 맞추면 바로 사용 가능하다
    send_mail(subject, message, settings.EMAIL_HOST_USER, to_email)
