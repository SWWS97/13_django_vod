from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.forms import CommentForm, BlogForm
from blog.models import Blog, Comment


class BlogListView(ListView):
    # model = Blog # 이렇게 정의하면 무조건 Blog.object.all()로 가져오게 됨
    # queryset = Blog.objects.all().order_by("-created_at")
    queryset = Blog.objects.all() # == model = Blog
    template_name = "blog/blog_list.html"
    paginate_by = 10
    ordering = ("-created_at", ) # == .order_by("-created_at") , list로 써도 동작에 문제는 없지만 immutable한 객체 이기 떄문에 튜플

    def get_queryset(self):
        queryset = super().get_queryset()

        q = self.request.GET.get("q")

        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )

        return queryset # blog_list.html에 object_list로 들어가고, 페이지 네이션 쪽엔 page_obj로 찾아서 들어가게 됨.


# prefetch_related : 쿼리 join
class BlogDetailView(ListView):
    model = Comment
    queryset = Blog.objects.all().prefetch_related("comment_set", "comment_set__author")
    template_name = "blog/blog_detail.html"
    paginate_by = 10
    # pk_url_kwarg = "id"

    def get(self, request, *args, **kwargs):
        self.object = get_object_or_404(Blog, pk=kwargs.get("blog_pk"))
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(blog=self.object).prefetch_related("author")

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(id__lte=50)

    # def get_object(self, queryset=None):
    #     object = super().get_object() # == object = self.model.object.get(pk=self.kwargs.get("pk"))
    #
    #     return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["blog"] = self.object

        return context

    # 아래 CommentCreateView와 같은 기능
    # def post(self, *args, **kwargs):
    #     comment_form = CommentForm(self.request.POST)
    #
    #     if not comment_form.is_valid():
    #         self.object = self.get_object()
    #         context = self.get_context_data(object=self.object)
    #         context["comment_form"] = comment_form
    #         return self.render_to_response(context)
    #
    #     if not self.request.user.is_authenticated:
    #         raise Http404
    #
    #     comment = comment_form.save(commit=False)
    #     # comment.blog = self.get_object()
    #     comment.blog_id = self.kwargs["pk"] # kwargs["pk"] : urls.py에 <int:pk> 이부분에서 가져옴
    #     comment.author = self.request.user
    #     comment.save()
    #
    #     return HttpResponseRedirect(reverse_lazy("blog:detail", kwargs={"pk": self.kwargs["pk"]}))


class BlogCreateView(LoginRequiredMixin, CreateView): # LoginRequiredMixin == @login_required()
    model = Blog
    template_name = "blog/blog_form.html"
    # fields = ("category", "title", "content")
    form_class = BlogForm
    # success_url = reverse_lazy("cb_blog_detail") # blog_list등 정적인 페이지로 갈때만 사용

    def form_valid(self, form):
        # blog = form.save(commit=False)
        # blog.author = self.request.user
        # blog.save()
        # self.object = blog
        # 위에랑 같은 코드
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


    # blog_detail(상세) 페이지로 이동할떄 위에 form_valid에서 생성되기 전엔 어디 pk값으로 가야할지 모르기 떄문에
    # blog_detail로 이동시에는 블로그가 생성되고 나중에 호출되는 get_success_url을 사용
    # models.py에 있는 Blog 모델에 get_absolute_url 함수 정의 하는걸로 대체 가능
    # def get_success_url(self):
    #     return reverse_lazy("cb_blog_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sub_title"] = "작성"
        context["btn_name"] = "생성"
        return context


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = "blog/blog_form.html"
    # fields = ("category", "title", "content")
    form_class = BlogForm

    # # Blog 모델에 get_absolute_url 함수로 대체함
    # def get_success_url(self): # == Blog 모델에 get_absolute_url 함수
    #     return reverse_lazy("cb_blog_detail", kwargs={"pk": self.object.pk})

    # def get_object(self, queryset=None): # get_object : 한개의 객체만 가져올 떄 사용 가능, 예) detail, update, delete
    #     self.object = super().get_object(queryset)
    #
    #     if self.object.author != self.request.user:
    #         raise Http404
    #     return self.object

    # 위에 get_object 함수와 같은 코드
    def get_queryset(self):
            queryset = super().get_queryset()
            if self.request.user.is_superuser:
                return queryset
            return queryset.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sub_title"] = "수정"
        context["btn_name"] = "수정"
        return context


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog

    def get_queryset(self):
            queryset = super().get_queryset()
            if not self.request.user.is_superuser:
                return queryset.filter(author=self.request.user)
            return queryset

    # 위의 Detail, Update와 다르게 Blog 모델에 정의된 get_absolute_url 함수는 detail 페이지로 가게끔 되어 있어서
    # delete(삭제) 하면 해당 블로그가 없기 때문에 따로 get_success_url로 blog_list로 이동시킴
    def get_success_url(self):
        return reverse_lazy("blog:list")


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def get(self, *args, **kwargs):
        raise Http404

    def form_valid(self, form):
        blog = self.get_blog()
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.blog = blog
        self.object.save()
        return HttpResponseRedirect(reverse("blog:detail", kwargs={"blog_pk": blog.pk}))


    def get_blog(self):
        pk = self.kwargs["blog_pk"]
        blog = get_object_or_404(Blog, pk=pk)
        return blog

# /comment/create/<int:blog_pk>/
