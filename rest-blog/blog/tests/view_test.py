from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Blog


class BlogViewTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(
            username="test",
            is_active=True,
        )

        Blog.objects.create(
            title="배포",
            content="본문",
            author=user,
        )

        future_published_at = timezone.now() + timedelta(days=30)

        Blog.objects.create(
            title="아직 배포 안됨",
            content="본문",
            author=user,
            published_at=future_published_at,
        )

    # 블로그 목록이 정상적으로 보여지는지 확인하는 테스트
    def test_blog_list(self):
        response = self.client.get(reverse("blog_list"))

        blog_list = Blog.objects.all()
        # status code
        self.assertEqual(response.status_code, 200)
        # context, 뷰에서 내려준 blog_list가 DB에서 가져온 Blog 전체 개수와 같은지 확인
        self.assertEqual(response.context.get("blog_list").count(), blog_list.count())

    # 로그인 안하면 글 생성 페이지를 볼 수 없다는 것을 확인하는 테스트
    def test_blog_create_not_login(self):
        response = self.client.get(reverse("blog_create"))
        # 로그인 안 하고 /create/로 접근하면 302 리다이렉트
        self.assertEqual(response.status_code, 302)
        # 리다이렉트 위치가 LOGIN_URL?next=/create/ 인지도 확인
        self.assertEqual(response["Location"], settings.LOGIN_URL + "?next=/create/")

    # 로그인 후 POST 요청을 3번 해보는 테스트
    def test_blog_create(self):
        user = User.objects.first()
        self.client.force_login(user) # force_login : 로그인 한것처럼 처리 시키는 메소드 함수

        blog_count = Blog.objects.count()

        response = self.client.post(
            reverse("blog_create"),
            data={
                "title" : "제목",
                "content" : "본문",
                "published_at" : ""
            }
        )

        self.assertEqual(response.status_code, 302) # 정상적으로 생성됨
        self.assertEqual(response["Location"], reverse("blog_list")) # 목록으로 리다이렉트
        self.assertEqual(blog_count + 1, Blog.objects.all().count()) # 블로그 개수 1 증가

        # 예약 발행 글은 DB에 저장되지만 공개 목록에는 나오지 않아야 한다는 테스트
        all_count = Blog.all_objects.count()

        self.client.post(
            reverse("blog_create"),
            data={
                "title": "제목",
                "content": "본문",
                "published_at": timezone.now() + timedelta(days=2)
            }
        )

        # 블로그 공개 리스트(Blog.objects) 개수는 그대로 → published_at이 미래라서 “아직 공개되지 않은 글”이므로 공개 목록에는 안 나옴
        self.assertEqual(blog_count + 1, Blog.objects.all().count()) # 위에서 생성된 카운트(목록 갯수) 그대로 가져옴
        self.assertEqual(all_count + 1, Blog.all_objects.count()) # 전체 개수(Blog.all_objects)는 증가 → DB에는 글이 저장됨

        self.client.post(
            reverse("blog_create"),
            data={
                "title": "제목",
                "content": "본문",
                "published_at": timezone.now() - timedelta(days=2)
            }
        )

        # 과거 날짜로 발행하면 즉시 공개되는 상태이므로 공개 목록 개수도 증가해야 한다.
        self.assertEqual(blog_count + 2, Blog.objects.all().count())
