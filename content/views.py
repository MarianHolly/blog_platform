from django.shortcuts import render
from django.views.generic import DetailView, ListView, TemplateView

from content.models import Article


# ==================================== BLOG PLATFORM ======================== #

class HomePageView(ListView):
    template_name = 'content/home.html'
    model = Article
    context_object_name = "articles"


class AboutPageView(TemplateView):
    template_name = 'content/about.html'


class ArticleListView(ListView):
    template_name = "content/article_list.html"
    model = Article
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    template_name = "content/article.html"
    model = Article
    context_object_name = "article"


