from django.contrib import admin

from post.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ...
