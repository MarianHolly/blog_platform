from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.template.context_processors import request
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import View, DetailView, ListView, TemplateView, CreateView, UpdateView, DeleteView

from accounts.mixins import AdministratorRequiredMixin, WriterRequiredMixin, WriterOrSuperAdminRequiredMixin
from accounts.models import Profile
from content.forms import ArticleForm, BulletinForm, ArticleEvaluationForm
from content.mixins import ArticleOwnerMixin
from content.models import Article, Bulletin, Subscription
from engagement.forms import CommentModelForm
from engagement.models import Comment, Like, ReadLater

# Article status constants
ARTICLE_STATUS_PUBLISHED = 'published'
ARTICLE_STATUS_DRAFT = 'draft'
ARTICLE_VISIBILITY_PUBLIC = 'public'
ARTICLE_VISIBILITY_PRIVATE = 'private'
ARTICLE_EVAL_PENDING = 'pending'
ARTICLE_EVAL_UNDER_REVIEW = 'under_review'
ARTICLE_EVAL_APPROVED = 'approved'
ARTICLE_EVAL_REJECTED = 'rejected'

# Profile role constants
PROFILE_ROLE_READER = 'reader'
PROFILE_ROLE_WRITER = 'writer'
PROFILE_ROLE_ADMIN = 'admin'

# ==================================== BLOG PLATFORM ======================== #

@method_decorator(cache_page(60 * 1), name='dispatch')
class HomePageView(ListView):
    template_name = "content/home.html"
    model = Article
    context_object_name = "featured_articles"
    paginate_by = 9

    def get_queryset(self):
        return Article.objects.filter(
            status=ARTICLE_STATUS_PUBLISHED
        ).select_related('bulletin__owner').order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        popular_bulletins = cache.get('popular_bulletins')
        if popular_bulletins is None:
            popular_bulletins = list(Bulletin.objects.all()[:3])
            cache.set('popular_bulletins', popular_bulletins, 60 * 2)

        recent_writers = cache.get('recent_writers')
        if recent_writers is None:
            recent_writers = list(Profile.objects.filter(role=PROFILE_ROLE_WRITER)[:3])
            cache.set('recent_writers', recent_writers, 60 * 2)  # 2 min

        context['popular_bulletins'] = Bulletin.objects.all()[:3]
        context['recent_writers'] = Profile.objects.filter(role=PROFILE_ROLE_WRITER)[:3]
        context['new_readers'] = Profile.objects.filter(role=PROFILE_ROLE_READER)[:3]
        return context


class AboutPageView(TemplateView):
    template_name = "content/about.html"


class QAPageView(TemplateView):
    template_name = "content/qa.html"


# ==================================== CONTENT RELATED ======================== #


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

        if self.request.user.is_authenticated:
            user_profile = self.request.user.profile

            is_liked = Like.objects.filter(
                article=article_,
                author=user_profile).exists()
            is_read_later = ReadLater.objects.filter(
                article=article_,
                author=user_profile).exists()
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user.profile,
                bulletin=article_.bulletin
            ).exists()

            context['is_subscribed'] = is_subscribed
            context['is_liked'] = is_liked
            context['is_read_later'] = is_read_later
        else:
            context['is_subscribed'] = False
            context['is_liked'] = False
            context['is_read_later'] = False

        context['comment_form'] = CommentModelForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        _article = self.object
        _profile = Profile.objects.get(user=self.request.user)
        comment_form = CommentModelForm(request.POST)

        if comment_form.is_valid():
            content = comment_form.cleaned_data['content']
            comment_qs = Comment.objects.filter(article=_article, author=_profile)

            if comment_qs.exists():
                comment = comment_qs.first()
                comment.content = content
                comment.save()
            else:
                Comment.objects.create(
                    article=_article,
                    author=_profile,
                    content=content,
                )

        return redirect(request.path)
        # return render(request, self.template_name, context)


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

    def form_invalid(self, form):
        if 'content' in form.errors:
            messages.error(self.request, "Článok nemôže byť uložený, pretože nemá žiadny obsah.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('bulletin_detail', kwargs={'slug': self.request.user.profile.bulletin.slug})


class ArticleUpdateView(ArticleOwnerMixin, LoginRequiredMixin, WriterRequiredMixin, UpdateView):
    template_name = "content/form.html"
    form_class = ArticleForm
    model = Article

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        if 'content' in form.errors:
            messages.error(self.request, "Článok nemôže byť uložený, pretože nemá žiadny obsah.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('article_detail', kwargs={'pk': self.object.id})


class ArticleDeleteView(LoginRequiredMixin, WriterOrSuperAdminRequiredMixin, DeleteView):
    template_name = "content/confirm_delete.html"
    model = Article

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.bulletin.owner.user.username})


# ==================================== BULLETIN RELATED ======================== #


class BulletinDetailView(ListView):
    template_name = "content/bulletin_detail.html"
    model = Article
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        self.bulletin = get_object_or_404(Bulletin, slug=self.kwargs['slug'])
        # Cache the queryset for this bulletin
        cache_key = f'bulletin_articles_{self.bulletin.id}_{self.request.GET.get("page", 1)}'
        articles = cache.get(cache_key)
        if articles is None:
            articles = self.bulletin.articles.filter(
                status=ARTICLE_STATUS_PUBLISHED
            ).select_related('bulletin__owner').order_by('-published')
            cache.set(cache_key, articles, 60 * 10)

        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bulletin'] = self.bulletin

        is_subscribed = None
        if self.request.user.is_authenticated:
            is_subscribed = Subscription.objects.filter(
                subscriber=self.request.user.profile,
                bulletin=self.bulletin
            ).exists()
        context['is_subscribed'] = is_subscribed

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
        context['drafts'] = bulletin.articles.filter(status=ARTICLE_STATUS_DRAFT)
        context['articles'] = bulletin.articles.filter(status=ARTICLE_STATUS_PUBLISHED)
        return context


# ==================================== SUBSCRIPTION ======================== #


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


# ==================================== WRITER FEATURES ======================== #


class ArticleVisibilityToggleView(LoginRequiredMixin, ArticleOwnerMixin, View):
    def get_object(self):
        return get_object_or_404(Article, id=self.kwargs['id'])

    def post(self, request, id):
        article = self.get_object()

        if article.visibility == ARTICLE_VISIBILITY_PUBLIC:
            article.visibility = ARTICLE_VISIBILITY_PRIVATE
        else:
            article.visibility = ARTICLE_VISIBILITY_PUBLIC
        article.save()

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('bulletin_dashboard', slug=article.bulletin.slug)


# ==================================== ADMIN FEATURES ======================== #


class ArticleEvaluationDashboardView(LoginRequiredMixin, AdministratorRequiredMixin, ListView):
    template_name = 'accounts/admin_dashboard.html'
    model = Article
    context_object_name = "articles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unreviewed_articles'] = Article.objects.filter(evaluation=ARTICLE_EVAL_UNDER_REVIEW)
        context['reviewed_articles'] = Article.objects.filter(evaluation__in=[ARTICLE_EVAL_APPROVED, ARTICLE_EVAL_REJECTED])
        return context


class ArticleEvaluationToggleView(LoginRequiredMixin, AdministratorRequiredMixin, View):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id)

        if article.evaluation == ARTICLE_EVAL_PENDING:
            article.evaluation = ARTICLE_EVAL_UNDER_REVIEW
            article.save()
            messages.success(request, f'{article.title} - je v procese hodnotenia.')
        else:
            messages.warning(request, f'{article.title} - je už v procese hodnotenia.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)


class ArticleEvaluationDecisionView(LoginRequiredMixin, AdministratorRequiredMixin, UpdateView):
    template_name = "accounts/evaluation_form.html"
    form_class = ArticleEvaluationForm
    model = Article
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('article_evaluation_dashboard')


# ==================================== FEATURES ======================== #

class ArticleSearchView(ListView):
    template_name = "content/search_results.html"
    model = Article
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query),
                status=ARTICLE_STATUS_PUBLISHED
            ).select_related('bulletin__owner')
        return Article.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        context['article_count'] = self.get_queryset().count()
        return context