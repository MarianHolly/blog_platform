from django.db.models import Model, DateTimeField, ForeignKey, TextField, CASCADE

from accounts.models import Profile
from content.models import Article


# Create your models here.
class Comment(Model):
    author = ForeignKey(Profile, on_delete=CASCADE, related_name='comments')
    article = ForeignKey(Article, on_delete=CASCADE, related_name='comments')
    content = TextField(max_length=500, blank=False, null=False)

    created = DateTimeField(auto_now_add=True)
    updated = DateTimeField(auto_now=True)

    def __repr__(self):
        return f"Comment(author={self.author}, article={self.article})"

    def __srt__(self):
        return f"{self.author} commented on {self.article}"


class Like(Model):
    author = ForeignKey(Profile, on_delete=CASCADE)
    article = ForeignKey(Article, on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"Like(author={self.author}, article={self.article})"

    def __srt__(self):
        return f"{self.author} liked {self.article}"


class ReadLater(Model):
    author = ForeignKey(Profile, on_delete=CASCADE)
    article = ForeignKey(Article, on_delete=CASCADE)
    created = DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f"ReadLater(author={self.author}, article={self.article})"

    def __srt__(self):
        return f"{self.author} read later on {self.article}"