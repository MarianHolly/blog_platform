from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView

from accounts.models import Profile
from content.forms import ArticleForm, BulletinForm
from content.models import Article, Bulletin, Subscription


# ==================================== BLOG PLATFORM ======================== #

class HomePageView(ListView):
    template_name = "content/home.html"
    model = Article
    context_object_name = "articles"

    """ Articles, Bulletins, Writers, Readers """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_articles'] = Article.objects.all()
        context['popular_bulletins'] = Bulletin.objects.all()
        context['recent_writers'] = Profile.objects.filter(role='writer')
        context['new_readers'] = Profile.objects.filter(role='reader')
        return context


def home(request):
    context = {
        'featured_articles': Article.objects.all(),
        'popular_bulletins': Bulletin.objects.all(),
        'recent_writers': Profile.objects.all(),
    }
    return render(request, "content/home.html", context)


class AboutPageView(TemplateView):
    template_name = "content/about.html"


class QAPAgeView(TemplateView):
    pass


# ==================================== ARTICLE RELATED ======================== #


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


# ==================================== BULLETIN RELATED ======================== #


class BulletinDetailView(DetailView):
    template_name = "content/bulletin_detail.html"
    model = Bulletin
    context_object_name = "bulletin"
    slug_field = "slug"
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """ Subscriptions """
        context = super().get_context_data(**kwargs)
        bulletin = self.get_object()

        if self.request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user.profile,
                bulletin=bulletin
            ).exists()

        context['is_subscribed'] = is_subscribed
        return context


class BulletinUpdateView(UpdateView):
    template_name = "accounts/profile_form.html"
    model = Bulletin
    form_class = BulletinForm
    success_url = reverse_lazy('article_list')
    slug_field = "slug"
    slug_url_kwarg = 'slug'


class BulletinListView(ListView):
    template_name = "content/bulletin_archive.html"
    model = Bulletin
    context_object_name = "bulletin"


def bulletin_archive(request, slug):
    bulletin_ = Bulletin.objects.get(slug=slug)
    articles_ = Article.objects.all().filter(bulletin=bulletin_)

    context = {
        'bulletin': bulletin_,
        'articles': articles_,
    }
    return render(request, 'content/bulletin_archive.html', context)


class SubscriptionToggleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        # get bulletin
        bulletin = get_object_or_404(Bulletin, slug=slug)
        user_profile = request.user.profile

        # if subscription exists
        subscription = Subscription.objects.filter(
            subscriber=user_profile,
            bulletin=bulletin)

        if subscription.exists():
            subscription.delete()
        else:
            Subscription.objects.create(
                subscriber=user_profile,
                bulletin=bulletin)

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)
