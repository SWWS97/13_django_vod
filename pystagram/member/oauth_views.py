from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core import signing
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.generic import RedirectView
import requests

from member.forms import NicknameForm

User = get_user_model()

NAVER_CALLBACK_URL = "/oauth/naver/callback/"
NAVER_STATE = "naver_login"
NAVER_LOGIN_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_PROFILE_URL = "https://openapi.naver.com/v1/nid/me"

# scheme : https, http를 가져옴 (개발환경에서 http, 배포환경에서 https로 요청 했을때)
class NaverLoginRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        domain = self.request.scheme + '://' + self.request.META.get('HTTP_HOST', '')

        callback_url = domain + NAVER_CALLBACK_URL
        state = signing.dumps(NAVER_STATE)

        params = {
            "response_type" : "code",
            "client_id" : settings.NAVER_CLIENT_ID,
            "redirect_uri" : callback_url,
            "state": state
        }

        return f'{NAVER_LOGIN_URL}?{urlencode(params)}'


def naver_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if NAVER_STATE != signing.loads(state):
        raise Http404

    access_token = get_naver_access_token(code, state)

    profile_response = get_naver_profile(access_token)

    print("profile request", profile_response)
    email = profile_response.get("email")

    user = User.objects.filter(email=email).first()

    if user:
        if not user.is_active:
            user.is_active = True
            user.save()

        login(request, user)
        return redirect("main")

    return redirect(
        reverse("oauth:nickname") + f"?access_token={access_token}"
    )


def oauth_nickname(request):
    access_token = request.GET.get("access_token")
    if not access_token:
        return redirect("login")

    form = NicknameForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)

        profile = get_naver_profile(access_token)
        email = profile.get("email")

        if User.objects.filter(email=email).exists():
            raise Http404

        user.email = email

        user.is_active = True
        raw_password = get_random_string(12)
        user.set_password(raw_password)
        user.save()

        login(request, user)
        return redirect("main")

    return render(request, "auth/nickname.html", {"form": form})


def get_naver_access_token(code, state):
    params = {
        "grant_type": "authorization_code",
        "client_id": settings.NAVER_CLIENT_ID,
        "client_secret": settings.NAVER_SECRET,
        "code": code,
        "state": state
    }

    response = requests.get(NAVER_TOKEN_URL, params=params)
    result = response.json()

    return result.get("access_token")


def get_naver_profile(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(NAVER_PROFILE_URL, headers=headers)

    if response.status_code != 200:
        raise Http404

    result = response.json()

    return result.get("response")
