from tabnanny import verbose
from venv import create

from core.models import Socio
from django.db import models
from django.utils.translation import gettext as _


class Issue(models.Model):
    STATUS_OPEN = 'OPEN'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_CLOSED, 'Closed'),
    )

    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MEDIUM'
    PRIORITY_HIGH = 'HIGH'
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    )

    CATEGORY_ASSOCIACAO = 'ASSOCIACAO'
    CATEGORY_ESPORTES = 'ESPORTES'
    CATEGORY_BATERIA = 'BATERIA'
    CATEGORY_EVENTOS = 'EVENTOS'
    CATEGORY_LOJA = 'LOJA'
    CATEGORY_OUTRA = 'OUTRA'
    CATEGORY_CHOICES = (
        (CATEGORY_ASSOCIACAO, 'Associação'),
        (CATEGORY_BATERIA, 'Bateria'),
        (CATEGORY_ESPORTES, 'Esportes'),
        (CATEGORY_EVENTOS, 'Eventos'),
        (CATEGORY_LOJA, 'Loja'),
        (CATEGORY_OUTRA, 'Outra'),
    )

    author = models.ForeignKey(
        'core.Socio',
        on_delete=models.CASCADE,
        related_name='issues',
        verbose_name=_('author'),
    )
    title = models.CharField(max_length=255, verbose_name=_('title'))
    description = models.TextField(verbose_name=_('description'))
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, verbose_name=_('status'), default=STATUS_OPEN)
    priority = models.CharField(
        max_length=255, choices=PRIORITY_CHOICES, verbose_name=_('priority'))
    category = models.CharField(
        max_length=255, choices=CATEGORY_CHOICES, verbose_name=_('category'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created at'))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_('updated at'))

    def __str__(self):
        return self.title

    def check_status(self):
        if self.comments.count() > 0 and not self.status == self.STATUS_CLOSED:
            self.status = self.STATUS_IN_PROGRESS

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']
        verbose_name = _('issue')
        verbose_name_plural = _('issues')


class Comment(models.Model):
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name='comments', verbose_name=_('issue'))
    author: Socio = models.ForeignKey(
        'core.Socio', on_delete=models.CASCADE, verbose_name=_('author'))
    description = models.TextField(verbose_name=_('description'))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created at'))

    def __str__(self):
        return self.description

    def get_author_apelido(self) -> str:
        return self.author.nickname

    class Meta:
        ordering = ['created_at']
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
