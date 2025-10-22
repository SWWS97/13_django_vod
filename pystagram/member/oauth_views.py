from django.conf import settings
from django.core import signing
from django.views.generic import RedirectView

NAVER_CALLBACK_URL = "/naver/callback"
NAVER_STATE = "naver_login"
NAVER_LOGIN_URL = "https://nid.naver.com/oauth2.0/authorize"

# scheme : https, http를 가져옴 (개발환경에서 http, 배포환경에서 https로 요청 했을때)
class NaverLoginRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        domain = self.request.scheme + "://" + self.request.META.get("HTTP_HOST", "")

        callback_url = domain + NAVER_CALLBACK_URL
        state = signing.dumps(NAVER_STATE)

        params = {
            "response_type" : "code",
            "client_id" : settings.NAVER_CLIENT_ID,
            "redirect_uri" : callback_url,
        }
