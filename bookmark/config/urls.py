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
from django.shortcuts import render, redirect
from django.urls import path

champion_list = [
    {"charactor": "가렌", "job" : "전사"},
    {"charactor": "럭스", "job" : "마법사"},
    {"charactor": "탈론", "job" : "암살자"},
    {"charactor": "사이온", "job" : "탱커"},
]

book_list = [
    {"title" : "그림으로 배우는 파이썬", "content" : "안녕하세요"},
    {"title" : "클린코드", "content" : "반갑습니다"},
    {"title" : "AWS", "content" : "누구세요?"},
    {"title" : "Django", "content" : "저에요"},
    {"title" : "FastAPI", "content" : "아하 그렇군요"},
    {"title" : "Flask", "content" : "네 반가워요"},
]

def book_all(request):

    context = {"books" : book_list}

    return render(request, "book_list.html", context)

def book_detail(request, index):
    if index > len(book_list):
        raise Http404

    book = book_list[index]
    context = {"book" : book}

    return render(request, "book_detail.html", context)


def champions(request):

    return render(request, "champion.html", {"champions": champion_list})

def champion_detail(request, index):
    if index > len(champion_list) -1:
        raise Http404

    champion = champion_list[index]
    context = {"champion" : champion}

    return render(request, "champion_detail.html", context)

def gugu(request, num):

    if num < 2:
        return redirect("/gugu/2/")

    context = {
        "num" : num,
        # "results" : [num * i for i in range(1, 10)]
        "results" : [(i, num * i) for i in range(1, 10)]
        # "range" : range(1, 10)
    }

    return render(request, "gugu.html", context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("champions/", champions, name="champions"),
    path("champion/<int:index>/", champion_detail, name="champions"),
    path("books/", book_all, name="books"),
    path("book/<int:index>/", book_detail, name="book"),
    path("gugu/<int:num>/", gugu, name="gugu"),
]
