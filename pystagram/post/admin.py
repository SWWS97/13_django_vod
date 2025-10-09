from django.contrib import admin

from post.models import PostImage, Post


# TabularInline : admin 페이지에서 1:N 관계 자식 모델을 “표 형식으로 한 화면에서 관리”하기 위한 클래스
class PostImageInline(admin.TabularInline):
    model = PostImage
    fields = ["image"]
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [
        PostImageInline,
    ]
