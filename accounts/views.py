from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, View, TemplateView, ListView

from accounts.forms import SignUpForm, ProfileForm
from accounts.mixins import ReaderRequiredMixin, AdministratorRequiredMixin
from accounts.models import Profile
from content.models import Article, Subscription
from engagement.models import Like, ReadLater

# Profile role constants
PROFILE_ROLE_READER = 'reader'
PROFILE_ROLE_WRITER = 'writer'
PROFILE_ROLE_ADMIN = 'admin'

# Create your views here.
class SignUpView(CreateView):
    """Create new user account and associated reader profile.

    Permissions:
    - Any anonymous user can create account (no authentication required)

    Behavior:
    - Creates new User and associated Profile with role='reader'
    - Auto-subscribes user to platform if configured
    - Redirects to login page after successful registration

    Returns:
    - Template context with signup form and validation errors
    - Redirect to login on successful creation
    """
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('login')


def logout_user(request):
    logout(request)
    return redirect('home')


class CustomLoginView(LoginView):
    """Authenticate user and create session.

    Permissions:
    - Any anonymous user can attempt login
    - Authenticated users are redirected to profile page

    Behavior:
    - Accepts username/password credentials
    - Creates session on successful authentication
    - Redirects already-authenticated users to their profile
    - Redirects successful login to user's profile page

    Returns:
    - Login form template for GET requests
    - Redirect to user's profile page on successful authentication
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class ProfileDetailView(DetailView):
    """Display user profile with subscriptions and recent activities.

    Permissions:
    - Any user can view any public profile
    - Shows toggle buttons only on own profile for authenticated users

    Behavior:
    - Loads user subscriptions (bulletins they follow)
    - Retrieves 5 most recent likes and read-later bookmarks
    - Conditionally shows role promotion buttons on user's own profile
    - Efficiently fetches related data with select_related

    Returns:
    - Profile object with subscriptions, recent_likes, recent_read_later lists
    - show_toggle_buttons context flag indicating if user viewing their own profile
    """
    template_name = 'accounts/profile.html'
    model = Profile
    context_object_name = "profile"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Subscriptions
        subscriptions = Subscription.objects.filter(
            subscriber=profile
        ).select_related('bulletin', 'bulletin__owner')
        context['subscriptions'] = subscriptions

        # Recent activities (5 of each type)
        recent_likes = Like.objects.filter(
            author=profile
        ).select_related('article__bulletin__owner').order_by('-created')[:5]

        recent_read_later = ReadLater.objects.filter(
            author=profile
        ).select_related('article__bulletin__owner').order_by('-created')[:5]

        context['recent_likes'] = recent_likes
        context['recent_read_later'] = recent_read_later

        # Only show toggle buttons on own profile
        context['show_toggle_buttons'] = (
                self.request.user.is_authenticated and
                self.request.user.profile == profile
        )
        return context


class ProfileActivityView(DetailView):
    """Display paginated user activity history (likes and read-later bookmarks).

    Permissions:
    - Any user can view activity of any public profile
    - Shows complete engagement history for the viewed user

    Query Optimization:
    - select_related('article__bulletin__owner'): Fetches article author in single query
    - Filters likes and read-laters by author, ordered by recency

    Behavior:
    - Paginates user's likes with 10 items per page (likes_page GET parameter)
    - Paginates user's read-later bookmarks with 10 items per page (read_later_page parameter)
    - Shows two separate paginated lists on single page
    - Efficiently fetches related article and bulletin data

    Returns:
    - Profile object with paginated likes_page_obj and read_later_page_obj
    - likes: Current page's list of user's likes
    - read_laters: Current page's list of user's bookmarks
    - Pagination objects for template navigation
    """
    template_name = 'accounts/profile_activity.html'
    model = Profile
    context_object_name = "profile"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        # Get page numbers for likes and read_later
        likes_page = self.request.GET.get('likes_page', 1)
        read_later_page = self.request.GET.get('read_later_page', 1)

        # Paginate likes
        likes_queryset = Like.objects.filter(author=profile).select_related('article__bulletin__owner').order_by('-created')
        likes_paginator = Paginator(likes_queryset, 10)
        likes_page_obj = likes_paginator.get_page(likes_page)

        # Paginate read later
        read_later_queryset = ReadLater.objects.filter(author=profile).select_related('article__bulletin__owner').order_by('-created')
        read_later_paginator = Paginator(read_later_queryset, 10)
        read_later_page_obj = read_later_paginator.get_page(read_later_page)

        context['likes'] = likes_page_obj.object_list
        context['likes_page_obj'] = likes_page_obj
        context['read_laters'] = read_later_page_obj.object_list
        context['read_later_page_obj'] = read_later_page_obj
        return context


class ProfileUpdateView(UpdateView):
    """Update user profile information (avatar, biography, etc.).

    Permissions:
    - LoginRequiredMixin not enforced; template/form should validate own-profile check
    - User can update their own profile via username URL parameter

    Behavior:
    - Allows editing profile fields (avatar, biography, etc.) via ProfileForm
    - User identified by URL username parameter (slug_field='user__username')
    - Redirects to updated profile on successful save
    - Form validation ensures only valid profile data is saved

    Returns:
    - Form with validation errors on invalid submission
    - Redirect to profile detail view on successful update
    """
    template_name = "accounts/profile_form.html"
    model = Profile
    form_class = ProfileForm
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.user.username})


class PromoteReaderToWriterView(LoginRequiredMixin, View):
    """Promote reader user to writer role (create personal bulletin).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - Self-service only: User can only promote their own account (enforced via username check)
    - Role restriction: Cannot promote if already writer or admin

    Behavior:
    - Validates requesting user is promoting their own account (matches URL username parameter)
    - Changes role from 'reader' to 'writer'
    - Creates personal Bulletin on first writer promotion (handled by post_save signal in models)
    - Displays success message on promotion, warning if already writer
    - Redirects to referrer if provided (via next POST parameter), otherwise to user's profile
    - Uses messages framework to provide user feedback

    Returns:
    - Redirect to profile page after successful promotion or error
    """
    def post(self, request, username):
        if request.user.username != username:
            messages.error(request, 'Nemôžeš meniť role iných používateľov.')
            return redirect('profile', username=request.user.username)

        profile = request.user.profile

        if profile.role == PROFILE_ROLE_READER:
            profile.role = PROFILE_ROLE_WRITER
            profile.save()
            messages.success(request, 'Stal si sa autorom.')
        elif profile.role == PROFILE_ROLE_WRITER:
            messages.warning(request, 'Už si autorom.')
        else:
            messages.warning(request, 'Chyba, pravdepodobne si adminom.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)


class PromoteReaderToAdminView(LoginRequiredMixin, View):
    """Promote reader user to administrator role (moderation privileges).

    Permissions:
    - LoginRequiredMixin: User must be authenticated
    - Superuser-only: Only Django superusers can promote users to admin role
    - Role restriction: Cannot promote writers (admin and writer are mutually exclusive roles)

    Behavior:
    - Validates requesting user is Django superuser (checked first)
    - Validates target user exists in database (raises 404-like messages if not)
    - Prevents promoting already-promoted users (warns if target already admin)
    - Prevents promoting writers (warns if target has writer role)
    - Changes role from 'reader' to 'admin' only if validation passes
    - Displays appropriate success/warning messages via messages framework
    - Redirects to referrer if provided (via next POST parameter), otherwise to user's profile
    - Gracefully handles non-existent users with error messages

    Returns:
    - Redirect to profile page after successful promotion or error
    """
    def post(self, request, username):
        # Only superusers can promote to admin
        if not request.user.is_superuser:
            messages.error(request, 'Nedostatočné oprávnenia pre túto akciu.')
            return redirect('profile', username=request.user.username)

        if request.user.username != username and not request.user.is_superuser:
            messages.error(request, 'Nemôžeš meniť role iných používateľov.')
            return redirect('profile', username=request.user.username)

        # Get target user profile
        try:
            target_user = User.objects.get(username=username)
            profile = target_user.profile
        except User.DoesNotExist:
            messages.error(request, 'Používateľ neexistuje.')
            return redirect('profile', username=request.user.username)

        if profile.role == PROFILE_ROLE_READER:
            profile.role = PROFILE_ROLE_ADMIN
            profile.save()
            messages.success(request, 'Stal si sa adminom.')

        elif profile.role == PROFILE_ROLE_WRITER:
            messages.warning(request, 'Nie je možné byť autorom a adminom zároveň.')
        else:
            messages.warning(request, 'Chyba, pravdepodobne si adminom.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)