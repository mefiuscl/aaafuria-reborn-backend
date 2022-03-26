from core.models import Socio
from django.db import models


class File(models.Model):
    author: Socio = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, blank=True, null=True)
    title: str = models.CharField(max_length=100, default='Untitled')
    content: str = models.TextField()
    url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    viewers = models.ManyToManyField(
        'core.Socio', related_name='files_viwers', blank=True)
    likes = models.ManyToManyField(
        'core.Socio', related_name='files_likes', blank=True)

    posted_at = models.DateTimeField(auto_now_add=True)

    is_hidden = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.author:
            self.author = Socio.objects.filter(
                user__username='22238742').first()
        super().save(*args, **kwargs)
