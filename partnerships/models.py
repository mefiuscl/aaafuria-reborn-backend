from core.models import Socio
from django.db import models


class Partnership(models.Model):
    name = models.CharField(max_length=60)
    socio_benefits = models.TextField()
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='partnerships/logos', blank=True, null=True)
    url = models.URLField(blank=True, null=True)
