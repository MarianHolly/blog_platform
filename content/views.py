from django.shortcuts import render


# Essential Views of Platform
def home(request):
    return render(request, "content/home.html")


def about(request):
    return render(request, "content/about.html")
