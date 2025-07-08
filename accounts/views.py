from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, View, TemplateView, ListView

from accounts.forms import SignUpForm, ProfileForm
from accounts.mixins import AdministratorRequiredMixin, ReaderRequiredMixin, WriterOrSuperAdminRequiredMixin
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
        """ Subscriptions + Recent Articles """
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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile_form.html"
    model = Profile
    form_class = ProfileForm
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        # Ensure users can only edit their own profile
        if request.user.username != kwargs.get('username'):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Profil bol úspešne aktualizovaný.')
            return response
        except Exception as e:
            messages.error(self.request, f'Chyba pri ukladaní profilu: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Formulár obsahuje chyby. Skontrolujte prosím zadané údaje.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.user.username})


class PromoteReaderToWriterView(LoginRequiredMixin, ReaderRequiredMixin, View):
    def post(self, request, username):
        profile = request.user.profile

        if profile.role == 'reader':
            profile.role = 'writer'
            profile.save()
            messages.success(request, 'Stal si sa autorom.')

        elif profile.role == 'writer':
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