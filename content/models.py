from django.db.models import Model, CharField, TextField, DateTimeField, ManyToManyField


# Create your models here.
class Category(Model):
    name = CharField(max_length=100, null=False, blank=False, unique=True)
    description = TextField(max_length=500, null=False, blank=False)

    def __repr__(self):
        return f"Category({self.name})"

    def __str__(self):
        return f"{self.name}"


class Article(Model):
    title = CharField(max_length=100, null=False, blank=False, unique=True)
    subtite = CharField(max_length=200, null=True, blank=True)
    description = TextField(null=True, blank=True)
    content = TextField(null=True, blank=True)

    created = DateTimeField(auto_now_add=True)
    published = DateTimeField(null=True, blank=True)
    updated = DateTimeField(auto_now=True)

    category = ManyToManyField(Category, related_name="articles")

    def __repr__(self):
        return f"Article(title={self.title}, author=Author, created={self.created})"

    def __str__(self):
        return f"{self.title} - Author - {self.created}"
