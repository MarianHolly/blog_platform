from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, View, TemplateView, ListView

from accounts.forms import SignUpForm, ProfileForm
from accounts.mixins import ReaderRequiredMixin, AdministratorRequiredMixin
from accounts.models import Profile
from content.models import Article, Subscription
from engagement.models import Like, ReadLater


# Create your views here.
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy('login')


def logout_user(request):
    logout(request)
    return redirect('home')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class ProfileDetailView(DetailView):
    template_name = 'accounts/profile.html'
    model = Profile
    context_object_name = "profile"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        """ Subscriptions """
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        subscriptions = Subscription.objects.filter(
            subscriber=profile
        ).select_related('bulletin', 'bulletin__owner')

        context['subscriptions'] = subscriptions

        # only show toggle buttons on own profile
        context['show_toggle_buttons'] = (
                self.request.user.is_authenticated and
                self.request.user.profile == profile
        )
        return context


class ProfileActivityView(DetailView):
    template_name = 'accounts/profile_activity.html'
    model = Profile
    context_object_name = "profile"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()

        likes = Like.objects.filter(author=profile)
        read_later = ReadLater.objects.filter(author=profile)
        context['likes'] = likes
        context['read_laters'] = read_later
        return context


class ProfileUpdateView(UpdateView):
    template_name = "accounts/profile_form.html"
    model = Profile
    form_class = ProfileForm
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.user.username})


class PromoteReaderToWriterView(LoginRequiredMixin, ReaderRequiredMixin, View):
    def post(self, request, username):
        profile = request.user.profile

        if profile.role == 'reader':
            profile.role = 'writer'
            profile.save()
            messages.success(request, 'Stal si sa autorom.')

        elif user_role == 'writer':
            messages.warning(request, 'Už si autorom.')
        else:
            messages.warning(request, 'Chyba, pravdepodobne si adminom.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)


class PromoteReaderToAdminView(LoginRequiredMixin, ReaderRequiredMixin, View):
    def post(self, request, username):
        profile = request.user.profile

        if profile.role == 'reader':
            profile.role = 'admin'
            profile.save()
            messages.success(request, 'Stal si sa adminom.')

        elif profile.role == 'writer':
            messages.warning(request, 'Nie je možné byť autorom a adminom zároveň.')
        else:
            messages.warning(request, 'Chyba, pravdepodobne si adminom.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('profile', username=request.user.username)


class ArticleEvaluationDashboardView(LoginRequiredMixin, AdministratorRequiredMixin, ListView):
    template_name = 'accounts/admin_dashboard.html'
    model = Article
    context_object_name = "articles"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unreviewed_articles'] = Article.objects.filter(evaluation='under_review')
        context['reviewed_articles'] = Article.objects.filter(evaluation__in=['approved', 'rejected'])
        return context