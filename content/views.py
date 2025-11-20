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
    """Display homepage with featured published articles and popular writers.

    Permissions:
    - Any user (authenticated or anonymous) can view

    Behavior:
    - Caches entire page response for 1 minute
    - Paginates published articles 9 per page
    - Fetches related bulletin and owner data efficiently
    - Loads popular bulletins (top 3) from cache (2 min TTL)
    - Loads recent writers with 'writer' role from cache (2 min TTL)
    - Shows new reader accounts (up to 3)

    Returns:
    - Paginated list of featured articles (published, newest first)
    - Popular bulletins (3 max)
    - Recent writers (3 max)
    - New readers (3 max)
    """
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
    """Display static about page with platform information.

    Permissions:
    - Any user can view

    Behavior:
    - Renders static template with no context data

    Returns:
    - Rendered about page template
    """
    template_name = "content/about.html"


class QAPageView(TemplateView):
    """Display static FAQ/Q&A page with help information.

    Permissions:
    - Any user can view

    Behavior:
    - Renders static template with no context data

    Returns:
    - Rendered Q&A page template
    """
    template_name = "content/qa.html"


# ==================================== CONTENT RELATED ======================== #


class ArticleListView(ListView):
    """Display list of all articles (no filtering applied).

    Permissions:
    - Any user can view

    Behavior:
    - Lists all articles from database without status filtering
    - Note: Templates may apply additional filtering

    Returns:
    - List of articles (potentially unfiltered)
    """
    template_name = "content/article_list.html"
    model = Article
    context_object_name = "articles"


class ArticleDetailView(DetailView):
    """Display article with engagement options (comments, likes, bookmarks).

    Permissions:
    - Any user can view published articles
    - Subscription/like/bookmark status only shown to authenticated users

    Behavior:
    - Loads article with related bulletin and owner data
    - For authenticated users:
      - Checks if user already liked the article
      - Checks if user already bookmarked (read-later) the article
      - Checks if user subscribed to the article's bulletin
    - Displays comment form for authenticated users
    - Handles POST requests to create/update user comments
    - One comment per user per article (update if exists)

    Returns:
    - Article object with engagement flags (is_liked, is_read_later, is_subscribed)
    - Comment form for rendering
    """
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
    """Create new article in user's bulletin.

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - WriterRequiredMixin: User must have 'writer' role

    Behavior:
    - Sets bulletin automatically to user's personal bulletin
    - Validates article content is not empty (rich text editor)
    - Allows draft or published status selection
    - Displays error message if content validation fails
    - Redirects to bulletin dashboard on successful creation

    Returns:
    - Form with validation errors on invalid submission
    - Redirect to bulletin detail on successful creation
    """
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
    """Update existing article (writers can only edit own bulletin articles).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - WriterRequiredMixin: User must have 'writer' role
    - ArticleOwnerMixin: Enforces article.bulletin == user's bulletin (prevents cross-bulletin edits)

    Behavior:
    - Retrieves article by primary key URL parameter
    - Validates article belongs to user's bulletin
    - Allows changing title, subtitle, description, content, status, visibility
    - Validates content field is not empty (rich text)
    - Displays error on content validation failure
    - Redirects to article detail on successful update

    Returns:
    - Form with validation errors on invalid submission
    - Redirect to article detail on successful update
    """
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
    """Delete article (writers delete own articles, admins can delete any).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - WriterOrSuperAdminRequiredMixin: User must be writer or superuser
    - Ownership: Writers can delete their own bulletin articles; superusers can delete any

    Behavior:
    - Retrieves article by primary key URL parameter
    - Displays deletion confirmation template
    - Performs cascade delete of article and related comments/likes/bookmarks
    - Redirects to article owner's profile on successful deletion

    Returns:
    - Confirmation template with article details
    - Redirect to profile on confirmed deletion
    """
    template_name = "content/confirm_delete.html"
    model = Article

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.bulletin.owner.user.username})


# ==================================== BULLETIN RELATED ======================== #


class BulletinDetailView(ListView):
    """Display bulletin (writer's publishing space) with published articles.

    Permissions:
    - Any user can view public bulletins

    Behavior:
    - Retrieves bulletin by slug from URL parameter
    - Paginates published articles (6 per page) ordered by publication date
    - Caches queryset per bulletin and page (10 min TTL)
    - For authenticated users: checks if subscribed to this bulletin
    - Efficiently fetches related bulletin owner data

    Returns:
    - Paginated list of published articles in the bulletin
    - Bulletin object details
    - is_subscribed flag (authenticated users only)
    """
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
    """Create new bulletin (writer's publishing space).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - WriterRequiredMixin: User must have 'writer' role
    - One bulletin per writer (enforced at profile level)

    Behavior:
    - Sets bulletin owner automatically to user's profile
    - Allows customizing title, description, and URL slug
    - Redirects to new bulletin on successful creation

    Returns:
    - Form with validation errors on invalid submission
    - Redirect to bulletin detail on successful creation
    """
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
    """Update bulletin details (title, description, slug).

    Permissions:
    - Any authenticated user can update (no mixin validation)
    - Note: Template/form should validate ownership

    Behavior:
    - Retrieves bulletin by primary key URL parameter
    - Allows editing bulletin metadata
    - Redirects to updated bulletin on successful save

    Returns:
    - Form with validation errors on invalid submission
    - Redirect to bulletin detail on successful update
    """
    template_name = "accounts/profile_form.html"
    model = Bulletin
    form_class = BulletinForm

    def get_success_url(self):
        return reverse('bulletin_detail', kwargs={'slug': self.request.user.profile.bulletin.slug})


class BulletinDashboardView(DetailView):
    """Display writer's dashboard with draft and published articles.

    Permissions:
    - Any user can view (no mixin validation)
    - Note: Template should restrict to bulletin owner only

    Behavior:
    - Retrieves bulletin by primary key URL parameter
    - Lists draft articles (unpublished/in-progress)
    - Lists published articles (live content)
    - Allows writers to manage their bulletin's content

    Returns:
    - Bulletin object with draft and published article lists
    """
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
    """Toggle user subscription to a bulletin (subscribe/unsubscribe).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - Self-service: Users can manage their own subscriptions
    - Prevents self-subscription: Cannot subscribe to own bulletin

    Behavior:
    - Retrieves bulletin by slug from URL parameter
    - Validates user is not bulletin owner
    - Creates subscription if doesn't exist
    - Deletes subscription if already exists
    - Shows success/warning messages accordingly
    - Redirects to referrer if provided, otherwise to own profile

    Returns:
    - Redirect to profile or referrer after toggling subscription
    """
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
    """Toggle article visibility between public and private.

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - ArticleOwnerMixin: User must own the article (bulletin match)

    Behavior:
    - Retrieves article by ID from URL parameter
    - Validates article ownership via ArticleOwnerMixin
    - Toggles visibility: public <-> private
    - Redirects to referrer if provided, otherwise to bulletin dashboard

    Returns:
    - Redirect to bulletin dashboard after toggling visibility
    """
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
    """Display admin dashboard for article evaluation and moderation.

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - AdministratorRequiredMixin: User must have 'admin' role

    Behavior:
    - Lists articles currently under review for evaluation
    - Lists articles already reviewed (approved or rejected)
    - Allows admins to evaluate submitted articles
    - Provides context for moderation workflow

    Returns:
    - All articles (unfiltered by default)
    - unreviewed_articles: Articles with 'under_review' evaluation status
    - reviewed_articles: Articles with 'approved' or 'rejected' status
    """
    template_name = 'accounts/admin_dashboard.html'
    model = Article
    context_object_name = "articles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unreviewed_articles'] = Article.objects.filter(evaluation=ARTICLE_EVAL_UNDER_REVIEW)
        context['reviewed_articles'] = Article.objects.filter(evaluation__in=[ARTICLE_EVAL_APPROVED, ARTICLE_EVAL_REJECTED])
        return context


class ArticleEvaluationToggleView(LoginRequiredMixin, AdministratorRequiredMixin, View):
    """Move article to under-review status for admin evaluation.

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - AdministratorRequiredMixin: User must have 'admin' role

    Behavior:
    - Retrieves article by ID from URL parameter
    - Changes evaluation status from 'pending' to 'under_review'
    - Prevents re-evaluating already-reviewed articles
    - Shows appropriate success/warning messages
    - Redirects to referrer if provided, otherwise to user's profile

    Returns:
    - Redirect to profile after status change
    """
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
    """Admin decision form for approving or rejecting articles under review.

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - AdministratorRequiredMixin: User must have 'admin' role

    Behavior:
    - Retrieves article by ID from URL parameter (pk_url_kwarg)
    - Displays form with two options: Approved or Rejected
    - Updates article evaluation status based on admin decision
    - Redirects to evaluation dashboard after decision

    Returns:
    - Form with approval/rejection options on GET
    - Redirect to evaluation dashboard on successful POST
    """
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
    """Search published articles by title or description.

    Permissions:
    - Any user can search

    Behavior:
    - Retrieves 'q' query parameter from GET request
    - Filters published articles by title or description (case-insensitive)
    - Paginates results 10 per page
    - Returns empty queryset if no query provided
    - Provides article count and query term to template

    Returns:
    - Paginated list of matching published articles
    - article_count: Total number of search results
    - query: The search term submitted by user
    """
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