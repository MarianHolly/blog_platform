from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from accounts.forms import SignUpForm, ProfileForm
from accounts.models import Profile


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
        return reverse_lazy('home')


class ProfileDetailView(DetailView):
    template_name = 'accounts/profile.html'
    model = Profile
    context_object_name = "profile"
    slug_field = 'user__username'
    slug_url_kwarg = 'username'


class ProfileUpdateView(UpdateView):
    template_name = "accounts/profile_form.html"
    model = Profile
    form_class = ProfileForm
    slug_field = 'user__username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.object.user.username})
