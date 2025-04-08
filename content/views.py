from django.shortcuts import render
from django.views.generic import DetailView, ListView

from content.models import Article


# Essential Views of Platform
def home(request):
    context = Article.objects.all()
    return render(request, "content/home.html", {"articles": context})


def about(request):
    return render(request, "content/about.html")


class ArticleDetailView(DetailView):
    template_name = "content/article.html"
    model = Article
    context_object_name = "article"
