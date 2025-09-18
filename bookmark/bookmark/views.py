from django.http import HttpResponse
from django.shortcuts import render

def bookmark_list(request):
    # return HttpResponse("<h1>북마크 리스트 페이지 입니다.</h1>")
    return render(request, "bookmark_list.html")


def bookmark_detail(request, num):

    context = {"num": num}

    return render(request, "bookmark_detail.html", context)