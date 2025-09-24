from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from blog.forms import BlogForm
from blog.models import Blog

# def blog_list(request):
#     blogs = Blog.objects.all().order_by("-created_at")

# visits = int(request.COOKIES.get("visits", 0)) + 1

# request.session["count"] = request.session.get("count", 0) + 1

# context = {
#     "blogs": blogs,
#     "count" : request.session["count"],
# }

# response = render(request, "blog/blog_list.html", context)
#
# response.set_cookie("visits", visits)

def blog_list(request):
    blogs = Blog.objects.all().order_by("-created_at")

    q = request.GET.get("q")
    if q:
        blogs = blogs.filter(
            Q(title__icontains=q) |
            Q(content__icontains=q)
        )

        # blogs = blogs.filter(content__icontains=q)

    paginator = Paginator(blogs, 10)
    page = request.GET.get("page")
    page_object = paginator.get_page(page)

    context = {
        "object_list" : page_object.object_list,
        "page_obj" : page_object,
    }

    return render(request, "blog/blog_list.html", context)


def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    context = {
        "blog" : blog,
    }

    return render(request, "blog/blog_detail.html", context)

@login_required()
def blog_create(request):
    # if not request.user.is_authenticated:
    #     return redirect((reverse("login")))

    form = BlogForm(request.POST or None)
    if form.is_valid():
        blog = form.save(commit=False) # blog 모델만 만들고 DB에 저장하지 않음
        blog.author = request.user
        blog.save() # DB 호출 DB에 저장
        return redirect(reverse("fb:detail", kwargs={"pk" : blog.pk}))


    context = {
        "form" : form,
    }

    return render(request, "blog/blog_create.html", context)


@login_required()
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk, author=request.user) # author(작성자)와 request(사용자)가 다르면 404

    # if request.user != blog.author:
    #     raise Http404

    # instance=blog : 이미 DB에 있는 Blog 객체를 가져와서 그걸 바탕으로 Form을 채우겠다는 뜻
    form = BlogForm(request.POST or None, instance=blog)
    if form.is_valid():
        blog = form.save() # form이 유효하면 DB에 저장
        return redirect(reverse("fb:detail", kwargs={"pk" : blog.pk}))

    context = {
        "form" : form,
    }

    return render(request, "blog/blog_update.html", context)

@login_required()
@require_http_methods(["POST"])
def blog_delete(request, pk):
    # if request.method != "POST":
    #     raise Http404
    blog = get_object_or_404(Blog, pk=pk, author=request.user)
    blog.delete()
    return redirect(reverse("fb:list"))


