from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView

from post.forms import PostForm, PostImageFormSet
from post.models import Post

# select_related : 1:N, 1:1 참조 컬럼 =>  “한쪽이 외래키로 참조하는 정방향 관계”
# prefetch_related : 1:N 역참조 컬럼, N:M 컬럼 => “역참조나 다대다(M2M)”
class PostListView(ListView):
    queryset = Post.objects.all().select_related("user").prefetch_related("images")
    template_name = "post/list.html"
    paginate_by = 5
    ordering = ("-created_at", )

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "post/form.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["formset"] = PostImageFormSet()
        return data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        image_formset = PostImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if image_formset.is_valid():
            image_formset.save()

        return HttpResponseRedirect(reverse("main"))

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "post/form.html"
    form_class = PostForm

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["formset"] = PostImageFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        self.object = form.save()

        image_formset = PostImageFormSet(self.request.POST, self.request.FILES, instance=self.object)
        if image_formset.is_valid():
            image_formset.save()

        return HttpResponseRedirect(reverse("main"))


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


# 클래스 인스턴스(객체) 비유
# 	•	📘 클래스 = 레시피(설계도)
# 	•	🍰 객체(인스턴스) = 그 레시피로 실제로 만든 케이크
# 	•	🎛️ 변수에 담기 = 케이크를 테이블 위에 올려두고 다루는 것
#
# PostImageFormSet은 “케이크를 만드는 레시피”에 불과하고,
# image_formset = PostImageFormSet(...) 하면
# 👉 실제 케이크가 만들어져서
# “맛보기(is_valid)”, “냉장보관(save)”, “조각내기(forms)” 같은 일을 할 수 있다.
