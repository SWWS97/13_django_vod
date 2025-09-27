from django.contrib import admin

from blog.models import Blog, Comment
from utils.models import TimeStampModel

# admin.site.register(Blog)
admin.site.register(Comment)

class CommentInline(admin.TabularInline):
    model = Comment
    fields = ["content", "author"]
    extra = 1

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline,
    ]

