from django.db import models as django_models


class News(django_models.Model):
    image = django_models.TextField(null=True, blank=True)
    header = django_models.TextField()
    content = django_models.TextField()
    link = django_models.TextField()
