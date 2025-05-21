from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import View

from content.models import Article
from engagement.models import Like, ReadLater


# Create your views here.
class LikeToggleView(LoginRequiredMixin, View):
    def post(self, request, id):
        # get article
        article = get_object_or_404(Article, id=id)
        user_profile = request.user.profile

        # check if user is not author of article
        if article.author == user_profile:
            messages.warning(request, "Nemôžeš dať like vlastnému článku.")
            next_url = request.POST.get('next', '')
            if next_url:
                return HttpResponseRedirect(next_url)
            return redirect(article.get_absolute_url())

        # if 'like' exists
        like = Like.objects.filter(article=article, author=user_profile)

        # toggle state of 'like'
        if like.exists():
            like.delete()
            messages.success(request, 'Odobral si like tomuto článku.')
        else:
            Like.objects.create(article=article, author=user_profile)
            messages.success(request, 'Dal si like tomuto článku.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect('article_detail', id=article.id )


class ReadLaterToggleView(LoginRequiredMixin, View):
    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        user_profile = request.user.profile

        if article.author == user_profile:
            messages.warning(request, "Nemôžeš označiť svoj článok ako prečítať neskôr.")
            next_url = request.POST.get('next', '')
            if next_url:
                return HttpResponseRedirect(next_url)
            return redirect(article.get_absolute_url())

        read_later = ReadLater.objects.filter(article=article, author=user_profile)

        if read_later.exists():
            read_later.delete()
            messages.success(request, 'Článok už nie je uložený na prečítanie.')
        else:
            ReadLater.objects.create(article=article, author=user_profile)
            messages.success(request, 'Článok je uložený na prečítanie neskôr.')

        next_url = request.POST.get('next', '')
        if next_url:
            return HttpResponseRedirect(next_url)
        return redirect(article.get_absolute_url())