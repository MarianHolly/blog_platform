from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.context_processors import request
from django.urls import reverse, reverse_lazy
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView

from accounts.models import Profile
from content.forms import ArticleForm, BulletinForm
from content.mixins import WriterRequiredMixin, ArticleOwnerMixin
from content.models import Article, Bulletin, Subscription


# ==================================== BLOG PLATFORM ======================== #

class HomePageView(ListView):
    template_name = "content/home.html"
    model = Article
    context_object_name = "articles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_articles'] = Article.objects.filter(status='published')
        context['popular_bulletins'] = Bulletin.objects.all()
        context['recent_writers'] = Profile.objects.filter(role='writer')
        context['new_readers'] = Profile.objects.filter(role='reader')
        return context


class AboutPageView(TemplateView):
    template_name = "content/about.html"


class QAPageView(TemplateView):
    template_name = "content/qa.html"


# ==================================== ARTICLE RELATED ======================== #


class ArticleListView(ListView):
    template_name = "content/article_list.html"
    model = Article
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    template_name = "content/article_detail.html"
    model = Article
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article_ = self.get_object()
        is_subscribed = None

        if self.request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user.profile,
                bulletin=article_.bulletin
            ).exists()

        context['is_subscribed'] = is_subscribed
        return context


class ArticleCreateView(LoginRequiredMixin, WriterRequiredMixin, CreateView):
    template_name = "content/form.html"
    form_class = ArticleForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Set bulletin automatically
        form.instance.bulletin = self.request.user.profile.bulletin
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bulletin_detail', kwargs={'slug': self.request.user.profile.bulletin.slug})


class ArticleUpdateView(LoginRequiredMixin, WriterRequiredMixin, UpdateView):
    template_name = "content/form.html"
    form_class = ArticleForm
    model = Article

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Errors:", form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('article_detail', kwargs={'pk': self.object.id})


class ArticleDeleteView(LoginRequiredMixin, WriterRequiredMixin, DeleteView):
    template_name = "content/confirm_delete.html"
    model = Article

    def get_success_url(self):
        return reverse('bulletin_dashboard', kwargs={'slug': self.request.user.profile.bulletin.slug})


# ==================================== BULLETIN RELATED ======================== #


class BulletinDetailView(DetailView):
    template_name = "content/bulletin_detail.html"
    model = Bulletin
    context_object_name = "bulletin"

    def get_context_data(self, **kwargs):
        """ Subscriptions """
        context = super().get_context_data(**kwargs)
        bulletin = self.get_object()
        is_subscribed = None

        if self.request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user.profile,
                bulletin=bulletin
            ).exists()

        context['is_subscribed'] = is_subscribed
        context['articles'] = bulletin.articles.filter(status='published')
        return context


class BulletinCreateView(LoginRequiredMixin, WriterRequiredMixin, CreateView):
    template_name = "content/bulletin_form.html"
    form_class = BulletinForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bulletin_detail', kwargs={'slug': self.request.user.profile.bulletin.slug})


class BulletinUpdateView(UpdateView):
    template_name = "accounts/profile_form.html"
    model = Bulletin
    form_class = BulletinForm

    def get_success_url(self):
        return reverse('bulletin_detail', kwargs={'slug': self.request.user.profile.bulletin.slug})


class BulletinDashboardView(DetailView):
    model = Bulletin
    template_name = "content/bulletin_dashboard.html"
    context_object_name = "bulletin"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bulletin = self.get_object()
        context['drafts'] = bulletin.articles.filter(status='draft')
        context['articles'] = bulletin.articles.filter(status='published')
        return context


# ==================================== ENGAGEMENT RELATED ======================== #


class ArticleVisibilityToggleView(LoginRequiredMixin, ArticleOwnerMixin, View):
    def get_object(self):
        return get_object_or_404(Article, id=self.kwargs['id'])

    def post(self, request, id):
        article = self.get_object()

        if article.visibility == 'public':
            article.visibility = 'private'
        else:
            article.visibility = 'public'
        article.save()

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('bulletin_dashboard', slug=article.bulletin.slug)


class SubscriptionToggleView(LoginRequiredMixin, View):
    def post(self, request, slug):
        # get bulletin
        bulletin = get_object_or_404(Bulletin, slug=slug)
        user_profile = request.user.profile

        # check if user is not owner of bulletin
        if bulletin.owner == user_profile:
            messages.warning(request, "Nemôžeš sa prihlásiť na svoj vlastný odber.")
            next_url = request.POST.get('next', '')
            if next_url:
                return HttpResponseRedirect(next_url)
            return redirect('bulletin_detail', slug=bulletin.slug)

        # if subscription exists
        subscription = Subscription.objects.filter(
            subscriber=user_profile,
            bulletin=bulletin
        )

        if subscription.exists():
            subscription.delete()
            messages.success(request, f'Zrušil si odber, {bulletin.title}')
        else:
            Subscription.objects.create(
                subscriber=user_profile,
                bulletin=bulletin
            )
            messages.success(request, f'Prihlásil si sa k odberu, {bulletin.title}')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)
