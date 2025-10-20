from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView

from post.forms import PostForm, PostImageFormSet, CommentForm
from post.models import Post, Like


# select_related : 1:N, 1:1 참조 컬럼 =>  “한쪽이 외래키로 참조하는 정방향 관계”
# prefetch_related : 1:N 역참조 컬럼, N:M 컬럼 => “역참조나 다대다(M2M)”
class PostListView(ListView):
    queryset = Post.objects.all().select_related("user").prefetch_related("images", "comments", "likes")
    template_name = "post/list.html"
    paginate_by = 5
    ordering = ("-created_at", )

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data["comment_form"] = CommentForm()

        return data


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


@csrf_exempt
@login_required()
def toggle_like(request):
    post_pk = request.POST.get("post_pk")
    if not post_pk:
        raise Http404()

    post = get_object_or_404(Post, pk=post_pk) # 해당 post를 가져오거나 없으면 404
    user = request.user # user는 로그인한 유저

    like, created = Like.objects.get_or_create(user=user, post=post) # DB에 있으면 가져오고, 없으면 새로 만든다

    if not created: # 생성 됐으면(좋아요를 눌렀으면)
        like.delete() # 좋아요 삭제

    return JsonResponse({"created": created}) # like 생성 했으면(좋아요를 눌렀으면) True, 아닐경우 False


# 클래스 인스턴스(객체) 비유
# 	•	📘 클래스 = 레시피(설계도)
# 	•	🍰 객체(인스턴스) = 그 레시피로 실제로 만든 케이크
# 	•	🎛️ 변수에 담기 = 케이크를 테이블 위에 올려두고 다루는 것
#
# PostImageFormSet은 “케이크를 만드는 레시피”에 불과하고,
# image_formset = PostImageFormSet(...) 하면
# 👉 실제 케이크가 만들어져서
# “맛보기(is_valid)”, “냉장보관(save)”, “조각내기(forms)” 같은 일을 할 수 있다.


def search(request):
    search_type = request.GET.get("type") # user, tag
    q = request.GET.get("q", '')
    print("search_type", search_type)
    print("q", q)

    if search_type in ["user", "tag"] and q:
        return render(request, f"search/search_{search_type}.html")

    return render(request, "search/search.html")
