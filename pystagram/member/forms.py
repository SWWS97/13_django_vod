from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

# password1, password2를 __init__을 오버라이딩해서 만들어 줌
class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # class_default_fields = ("password1", "password2")

        for field in ("password1", "password2"):
            self.fields[field].widget.attrs["class"] = "form-control"
            self.fields[field].widget.attrs["placeholder"] = "password"

            if field == "password1":
                self.fields[field].label = "비밀번호"
            else:
                self.fields[field].label = "비밀번호 확인"

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "nickname", )
        labels = {
            "email": "이메일",
            "nickname": "닉네임",
        }
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "example@example.com",
                    "class": "form-control",
                }
            ),
            "nickname": forms.TextInput(
                attrs={
                    "placeholder": "닉네임",
                    "class": "form-control",
                }
            )
        }

class LoginForm(forms.Form):
    email = forms.CharField(
        label="이메일",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "example@example.com",
                "class": "form-control",
            }
        )
    )

    # PasswordInput: 비밀번호 입력할 때 ******* 처리
    password = forms.CharField(
        label="패스워드",
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "password",
                "class": "form-control",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None


    # def clean(): Form 클래스에서 전체 필드(여러 입력값)를 한 번에 검사할 때 실행되는 메서드
    # 즉, email, password 둘 다 확인해야 할 때 clean()을 씀
    # 로그인 시 입력된 email, password가 유효한지 검사(clean)
    # 로그인 폼에서 사용자가 쓴 이메일/비밀번호가 맞는지 확인하고, 아직 인증되지 않은 계정이면 로그인 막기
    # cleaned_data = super().clean(): 부모 클래스(forms.Form)의 clean()을 먼저 실행해서 사용자가 입력한 데이터를 기본 검증 후 가져옴
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        # authenticate() : DB 내부를 조회해서 해당 이메일/비밀번호로 로그인 가능한 유저가 있는지 확인
        # 맞으면 User 객체 반환, 틀리면 None 반환
        self.user = authenticate(email=email, password=password)
        # 유저가 존재하긴 하지만 이메일 인증이 안 됐거나 비활성화된 계정
        if not self.user.is_active:
            raise forms.ValidationError("유저가 인증되지 않았습니다.")
        return cleaned_data # 모든 검증이 끝났다면 정제(cleaned)된 데이터를 반환
