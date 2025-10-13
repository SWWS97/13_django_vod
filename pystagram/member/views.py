from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core import signing
from django.core.signing import TimestampSigner, SignatureExpired
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, DetailView

from member.forms import SignupForm, LoginForm
from utils.email import send_email

User = get_user_model()

class SignupView(FormView):
    template_name = "auth/signup.html"
    form_class = SignupForm
    # success_url = reverse_lazy("signup_done")

    # signer: TimestampSigner 모듈을 가져옴
    # signed_user_email: 서명(Signature)을 덧붙여 위변조를 방지 => ex) test@example.com:1q2w3e4r5t6y7u8i9o0p
    # signer_dump: signing 모듈은 "데이터 위변조 방지"용이지, "데이터 암호화"는 아님
    # email 데이터를 안전하게 직렬화(serialize) + 서명(sign) => 조작 불가한 문자열로 변환 ex) eyJfX3NpZ25hdHVyZSI6ICJkY...
    # decoded_user_email: 직렬화된 문자열을 다시 원래 객체로 되돌림 => ex) test@example.com:1q2w3e4r5t6y7u8i9o0p
    # 원본 데이터로 돌려줌 => ex) "test@example.com"
    # unsign: max_age(초단위) 속성을 넣을수도 있음 => max_age=60 : 60초 이내만 유효

    def form_valid(self, form):
        user = form.save()
        # 이메일 발송
        signer = TimestampSigner()
        signed_user_email = signer.sign(user.email)
        # print(signed_user_email)

        signer_dump = signing.dumps(signed_user_email)
        # print(signer_dump)

        # decoded_user_email = signing.loads(signer_dump)
        # print(decoded_user_email)

        # email = signer.unsign(decoded_user_email, max_age=60 * 30)
        # print(email)

        # 현재 요청(request)의 정보를 이용해서 인증 링크(URL)을 동적으로 만드는 코드
        # http://localhost:8000/verify/?code=fasfsafsf : 로컬 환경
        # https://배포도메인/verify/?code=fasfsafsf : 배포 환경
        # scheme: 프로토콜(http, https)
        # META: Django의 요청 헤더와 서버 환경정보가 담긴 딕셔너리, "HTTP_HOST" => 클라이언트(브라우저)가 요청을 보낸 호스트 주소
        url = f"{self.request.scheme}://{self.request.META['HTTP_HOST']}/verify/?code={signer_dump}"
        if settings.DEBUG:
            print(url)
        else:
            subject = "[Pystagram]이메일 인증을 완료해주세요."
            message = f"다음 링크를 클릭해주세요. <br><a href='{url}'>{url}</a>"

            send_email(subject, message, user.email)

        return render(
            self.request,
            template_name="auth/signup_done.html",
            context={"user": user},
        )


def verify_email(request):
    code = request.GET.get("code", "") # 원래는 default == None => 여기선 "" 공백으로 넣어줌

    signer = TimestampSigner()
    try:
        decoded_user_email = signing.loads(code)
        email = signer.unsign(decoded_user_email, max_age=60 * 30)
    except (TypeError, SignatureExpired): # SignatureExpired : 인증 유효시간 지났을 때 에러 반환
        return render(request, "auth/not_verified.html")

    user = get_object_or_404(User, email=email, is_active=False) # 활성화 안된 객체만 가져옴
    user.is_active = True # 여기서 활성화 시킴
    user.save() # 데이터 베이스 저장
    return redirect(reverse("login"))
    # return render(request, "auth/email_verified_done.html", {"user": user})

class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("main")

    def form_valid(self, form):
        user = form.user
        login(self.request, user)

        next_page = self.request.GET.get("next")
        if next_page:
            return HttpResponseRedirect(next_page)

        return HttpResponseRedirect(self.get_success_url())


# 1️⃣ 사용자가 로그인 폼에서 이메일/비밀번호 입력
# ↓
# 2️⃣ LoginForm.clean() 실행 → DB에서 유저 존재 여부 확인
# ↓
# 3️⃣ 로그인 성공 시 self.user = user 로 저장
# ↓
# 4️⃣ 뷰(LoginView)에서 form.user 바로 꺼내서 로그인 처리
#
# 👉 즉, “한 번 DB에서 가져온 유저 정보를 다시 불러올 필요 없음”
# 왜냐면 이미 form이 들고 있으니까 DB 쿼리 최소화 시킴


# url에서 기본값은 pk로 가져오게 되는데 nickname으로 받고 싶으니
# slug_field(여기선 url에서 slug_url_kwarg에 해당하는 값을 보고 유저 컬럼에서 해당 유저의 nickname을 가져옴)
# 기본값인 pk_url_kwarg = "pk" 이거 대신 slug_url_kwarg = "slug"
# profile/<str:slug>/ => 예) profile/admin/ => User모델의 nickname(admin)을 가져옴
class UserProfileView(DetailView):
    model = User
    template_name = "profile/detail.html"
    slug_field = "nickname"
    slug_url_kwarg = "slug"
    queryset = User.objects.all().prefetch_related("post_set", "post_set__images")
