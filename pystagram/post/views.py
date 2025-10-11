from django.shortcuts import render
from django.views.generic import ListView

from post.models import Post

# select_related : 1:N 참조 컬럼 =>  “한쪽이 외래키로 참조하는 정방향 관계”
# prefetch_related : 1:N 역참조 컬럼, N:M 컬럼 => “역참조나 다대다(M2M)”
class PostListView(ListView):
    queryset = Post.objects.all().select_related("user").prefetch_related("images")
    template_name = "post/list.html"
    paginate_by = 5
    ordering = ("-created_at", )
