from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.models import Blog


class BlogListView(ListView):
    # model = Blog # 이렇게 정의하면 무조건 object.all()로 가져오게 됨
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


class BlogDetailView(DetailView):
    model = Blog
    template_name = "blog/blog_detail.html"
    # pk_url_kwarg = "id"

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(id__lte=50)

    # def get_object(self, queryset=None):
    #     object = super().get_object() # == object = self.model.object.get(pk=self.kwargs.get("pk"))
    #
    #     return object

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["test"] = "CBV"
    #
    #     return context

class BlogCreateView(LoginRequiredMixin, CreateView): # LoginRequiredMixin == @login_required()
    model = Blog
    template_name = "blog/blog_create.html"
    fields = ("title", "content")
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


class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = "blog/blog_update.html"
    fields = ("title", "content")

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
        return queryset.filter(author=self.request.user)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    # 위의 Detail, Update와 다르게 Blog 모델에 정의된 get_absolute_url 함수는 detail 페이지로 가게끔 되어 있어서
    # delete(삭제) 하면 해당 블로그가 없기 때문에 따로 get_success_url로 blog_list로 이동시킴
    def get_success_url(self):
        return reverse_lazy("blog_list")





