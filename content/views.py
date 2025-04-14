from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView

from content.forms import ArticleForm
from content.models import Article, Bulletin


# ==================================== BLOG PLATFORM ======================== #

class HomePageView(ListView):
    template_name = "content/home.html"
    model = Article
    context_object_name = "articles"


class AboutPageView(TemplateView):
    template_name = "content/about.html"


class ArticleListView(ListView):
    template_name = "content/article_list.html"
    model = Article
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    template_name = "content/article_detail.html"
    model = Article
    context_object_name = "article"


class ArticleCreateView(CreateView):
    template_name = "content/form.html"
    form_class = ArticleForm
    success_url = reverse_lazy("article_list")


class ArticleUpdateView(UpdateView):
    template_name = "content/form.html"
    form_class = ArticleForm
    model = Article
    success_url = reverse_lazy("article_list")


class ArticleDeleteView(DeleteView):
    template_name = "content/confirm_delete.html"
    model = Article
    success_url = reverse_lazy('article_list')


class BulletinDetailView(DetailView):
    model = Bulletin
    template_name = "content/bulletin_detail.html"
    context_object_name = "bulletin"
    slug_field = "slug"
    slug_url_kwarg = 'slug'


class BulletinListView(ListView):
    template_name = "content/bulletin_archive.html"
    model = Article
    context_object_name = "articles"
    extra_context = ""