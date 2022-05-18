from django.db import models
from django.utils.translation import gettext as _


class Partnership(models.Model):
    name = models.CharField(max_length=60, verbose_name=_('name'))
    socio_benefits = models.TextField(verbose_name=_('socio benefits'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description'))
    logo = models.ImageField(
        upload_to='partnerships/logos', blank=True, null=True, verbose_name=_('logo'))
    url = models.URLField(blank=True, null=True, verbose_name=_('url'))

    class Meta:
        verbose_name = _('partnership')
        verbose_name_plural = _('partnerships')

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
