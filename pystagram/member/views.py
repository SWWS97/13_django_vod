from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.signing import TimestampSigner, SignatureExpired
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView

from member.forms import SignupForm
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
    # TODO: 나중에 Redirect 시키기
    # return redirect(reverse("login"))
    return render(request, "auth/email_verified_done.html", {"user": user})