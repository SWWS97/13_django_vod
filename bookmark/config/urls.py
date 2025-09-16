"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.urls import path

champion_list = [
    {"charactor": "가렌", "job" : "전사"},
    {"charactor": "럭스", "job" : "마법사"},
    {"charactor": "탈론", "job" : "암살자"},
    {"charactor": "사이온", "job" : "탱커"},
]

def champions(request):

    return render(request, "champion.html", {"champions": champion_list})

def champion_detail(request, index):
    if index > len(champion_list) -1:
        raise Http404

    champion = champion_list[index]

    return render(request, "champion_detail.html", {"champion": champion})

urlpatterns = [
    path('admin/', admin.site.urls),
    path("champions/", champions, name="champions"),
    path("champion/<int:index>/", champion_detail, name="champions"),
]
