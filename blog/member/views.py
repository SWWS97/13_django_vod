from django.conf import settings # 현재 장고가 실행되고 있는 경로 환경에서 세팅 값을 알아서 찾아서 가져옴.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as django_login
from django.shortcuts import render, redirect
from django.urls import reverse


def sign_up(request):
    # 딕셔너리 get 함수 : dict.get(key, default=None), 지정 안 하면 None을 돌려줌.
    # 여기서 dict는 클라이언트가 회원가입 폼에 입력한 QueryDict에서 가져옴.
    # username = request.POST.get("username")
    # password1 = request.POST.get("password1")
    # password2 = request.POST.get("password2")
    #
    # print("username", username)
    # print("password1", password1)
    # print("password2", password2)

    # username 중복 확인 작업
    # 패스워드가 맞는지, 그리고 패스워드 정책에 올바른지 (대소문자)
    # UserCreationForm() : 장고에서 기본적으로 제공 해주는 회원가입 관련 폼(양식)

    # if request.method == "POST":
    #     form = UserCreationForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return redirect("/accounts/login/")
    # else:
    #     form = UserCreationForm() # GET 요청이면 새 회원가입 폼을 보여주고 valid 하지 않은 입력값일 경우 에러를 담은 폼을 보여줌.

    form = UserCreationForm(request.POST or None) # 입력된 값이 없으면 빈 양식을 폼에 저장

    if form.is_valid(): # form이 valid 하지 않으면 error(dict 형태: add_error 메서드 동작) 메시지를 폼에 저장
        form.save()
        return redirect(settings.LOGIN_URL)

    context = {
        "form" : form,
    }

    return render(request, "registration/signup.html", context)


def login(request):
    form = AuthenticationForm(request, request.POST or None)

    if form.is_valid():
        django_login(request, form.get_user())

        next = request.GET.get("next")
        if next:
            return redirect(next)

        return redirect(reverse("blog:list")) # reverse함수 : urls.py에 명시한 name으로 url을 찾아서 가져옴.

    context = {
        "form": form,
    }

    return render(request, "registration/login.html", context)