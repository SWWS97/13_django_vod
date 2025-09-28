from django import forms

from blog.models import Blog, Comment


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ("title", "content")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content", )
        widgets = {
            "content": forms.TextInput(attrs={"class": "form-control"}),
        }
        labels = {
            "content": "댓글",
        }
# widgets: fields 속성 설정, TextInput: input 태그로 만듦, attrs: input 태그 안에 속성 추가
# labels : Form에서 사용할 fields 이름 변경