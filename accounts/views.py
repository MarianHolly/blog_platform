from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from accounts.forms import SignUpForm
from accounts.models import Profile


# Create your views here.
class SignUpView(CreateView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('home')


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "profile.html"
    context_object_name = "profile"